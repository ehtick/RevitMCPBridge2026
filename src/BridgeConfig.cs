using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using Serilog;

namespace RevitMCPBridge
{
    /// <summary>
    /// Machine/firm-specific configuration for the bridge (bridge_config.json).
    ///
    /// This is the home for everything that used to be hardcoded personal data:
    /// local library/template paths, family search roots, firm sheet-numbering
    /// profiles, licensed-professional info, etc. NO personal or client data may
    /// be compiled into the DLL — it all lives in this config file.
    ///
    /// Load order (first file found wins):
    ///   1. bridge_config.json next to the deployed DLL
    ///   2. %APPDATA%\RevitMCPBridge\bridge_config.json
    ///
    /// Missing file and missing keys are always tolerated: path-style settings
    /// fall back to neutral defaults (DLL-adjacent or %APPDATA%\RevitMCPBridge
    /// subfolders), while library/template/search paths and firm profiles
    /// default to EMPTY — methods that need them return a clear "configure
    /// bridge_config.json" error instead of probing personal drive layouts.
    ///
    /// See CONFIG.md / bridge_config.sample.json at the repo root for the schema.
    /// </summary>
    public static class BridgeConfig
    {
        private static readonly object _lock = new object();
        private static JObject _config;
        private static string _loadedFrom;

        /// <summary>Name used both for the config file and the %APPDATA% folder.</summary>
        public const string ConfigFileName = "bridge_config.json";

        #region Loading

        private static JObject Config
        {
            get
            {
                if (_config == null)
                {
                    lock (_lock)
                    {
                        if (_config == null)
                        {
                            _config = LoadConfig();
                        }
                    }
                }
                return _config;
            }
        }

        /// <summary>Where the active config was loaded from ("(defaults)" if no file found).</summary>
        public static string LoadedFrom
        {
            get { var _ = Config; return _loadedFrom ?? "(defaults)"; }
        }

        /// <summary>Force a re-read of bridge_config.json on next access.</summary>
        public static void Reload()
        {
            lock (_lock) { _config = null; _loadedFrom = null; }
        }

        private static JObject LoadConfig()
        {
            var candidates = new[]
            {
                Path.Combine(DllDirectory, ConfigFileName),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                    "RevitMCPBridge", ConfigFileName)
            };

            foreach (var path in candidates)
            {
                try
                {
                    if (!File.Exists(path)) continue;
                    var parsed = JObject.Parse(File.ReadAllText(path));
                    _loadedFrom = path;
                    Log.Information("[BridgeConfig] Loaded {Path}", path);
                    return parsed;
                }
                catch (Exception ex)
                {
                    Log.Warning(ex, "[BridgeConfig] Failed to read {Path} — trying next location", path);
                }
            }

            Log.Information("[BridgeConfig] No bridge_config.json found — using neutral defaults " +
                            "(library/template/firm settings empty until configured)");
            return new JObject();
        }

        #endregion

        #region Generic accessors

        /// <summary>Get a string by dotted path (e.g. "paths.logDirectory"). Empty string when unset.</summary>
        public static string GetString(string path, string fallback = "")
        {
            try
            {
                var token = Config.SelectToken(path);
                var value = token?.Type == JTokenType.String ? token.ToString() : token?.ToString();
                return string.IsNullOrWhiteSpace(value) ? fallback : value;
            }
            catch { return fallback; }
        }

        /// <summary>Get a string array by dotted path. Empty array when unset.</summary>
        public static string[] GetStringList(string path)
        {
            try
            {
                if (Config.SelectToken(path) is JArray arr)
                    return arr.Select(t => t?.ToString())
                              .Where(s => !string.IsNullOrWhiteSpace(s))
                              .ToArray();
            }
            catch { /* tolerate malformed keys */ }
            return Array.Empty<string>();
        }

        /// <summary>Get an object by dotted path. Empty JObject when unset.</summary>
        public static JObject GetJObject(string path)
        {
            try
            {
                if (Config.SelectToken(path) is JObject obj) return obj;
            }
            catch { /* tolerate malformed keys */ }
            return new JObject();
        }

        /// <summary>Get a string→string map by dotted path. Empty map when unset.</summary>
        public static Dictionary<string, string> GetStringMap(string path)
        {
            var map = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            try
            {
                foreach (var prop in GetJObject(path).Properties())
                {
                    var v = prop.Value?.ToString();
                    if (!string.IsNullOrWhiteSpace(v)) map[prop.Name] = v;
                }
            }
            catch { /* tolerate malformed keys */ }
            return map;
        }

        #endregion

        #region Default locations

        /// <summary>Directory the bridge DLL is running from.</summary>
        public static string DllDirectory
        {
            get
            {
                try { return Path.GetDirectoryName(typeof(BridgeConfig).Assembly.Location) ?? ""; }
                catch { return ""; }
            }
        }

        /// <summary>%APPDATA%\RevitMCPBridge — the neutral home for bridge-generated data.</summary>
        public static string AppDataRoot =>
            EnsureDir(Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "RevitMCPBridge"));

        private static string EnsureDir(string path)
        {
            try { if (!string.IsNullOrEmpty(path)) Directory.CreateDirectory(path); }
            catch { /* read-only environments still get the path back */ }
            return path;
        }

        #endregion

        #region Typed settings — paths

        /// <summary>Where bridge log/progress files go. Default: %APPDATA%\RevitMCPBridge\logs.</summary>
        public static string LogDirectory
        {
            get
            {
                var configured = GetString("paths.logDirectory");
                return !string.IsNullOrEmpty(configured) ? EnsureDir(configured)
                                                         : EnsureDir(Path.Combine(AppDataRoot, "logs"));
            }
        }

        /// <summary>Self-expanding capability system root. Default: %APPDATA%\RevitMCPBridge\capability_system.</summary>
        public static string CapabilitySystemDirectory
        {
            get
            {
                var configured = GetString("paths.capabilitySystemDirectory");
                return !string.IsNullOrEmpty(configured) ? EnsureDir(configured)
                                                         : EnsureDir(Path.Combine(AppDataRoot, "capability_system"));
            }
        }

        /// <summary>
        /// Knowledge base root (firm profiles, extracted rules, agent knowledge files).
        /// Default: a "knowledge" folder next to the DLL if present, else %APPDATA%\RevitMCPBridge\knowledge.
        /// </summary>
        public static string KnowledgeDirectory
        {
            get
            {
                var configured = GetString("paths.knowledgeDirectory");
                if (!string.IsNullOrEmpty(configured)) return configured;
                var beside = Path.Combine(DllDirectory, "knowledge");
                if (Directory.Exists(beside)) return beside;
                return Path.Combine(AppDataRoot, "knowledge");
            }
        }

        /// <summary>Workflow template directory override. Empty = probe next to the DLL.</summary>
        public static string WorkflowsDirectory => GetString("paths.workflowsDirectory");

        /// <summary>Automation scripts directory override. Empty = probe next to the DLL.</summary>
        public static string ScriptsDirectory => GetString("paths.scriptsDirectory");

        /// <summary>Extra folders to scan for .rte project templates. Default: none.</summary>
        public static string[] TemplateSearchPaths => GetStringList("paths.templateSearchPaths");

        /// <summary>Where saveAsTemplate writes firm templates. Default: empty (must be configured).</summary>
        public static string FirmTemplatesDirectory => GetString("paths.firmTemplatesDirectory");

        /// <summary>Default shared-parameters .txt file for smart templates. Default: empty (must be configured).</summary>
        public static string SharedParametersFile => GetString("paths.sharedParametersFile");

        /// <summary>Root of the indexed detail/family library. Default: empty (must be configured).</summary>
        public static string LibraryRootDirectory => GetString("paths.libraryRootDirectory");

        /// <summary>The "Revit Details" folder used by detail/batch-text methods. Default: empty (must be configured).</summary>
        public static string DetailLibraryDirectory => GetString("paths.detailLibraryDirectory");

        /// <summary>Detail libraries searched by findCompatibleDetails, in preference order. Default: none.</summary>
        public static string[] DetailLibrarySearchPaths => GetStringList("paths.detailLibrarySearchPaths");

        /// <summary>Detail Library window default profile paths (keys: Details, Families, Legends, Schedules).</summary>
        public static Dictionary<string, string> LibraryProfilePaths => GetStringMap("paths.libraryProfilePaths");

        /// <summary>Roots the agent's search_files tool may scan when no path is given. Default: none.</summary>
        public static string[] FileSearchRoots => GetStringList("paths.fileSearchRoots");

        #endregion

        #region Typed settings — families

        /// <summary>Candidate .rfa files loaded when a door is requested and none is loaded. Default: none.</summary>
        public static string[] DefaultDoorFamilies => GetStringList("families.defaultDoorFamilies");

        /// <summary>Candidate .rfa files loaded when a window is requested and none is loaded. Default: none.</summary>
        public static string[] DefaultWindowFamilies => GetStringList("families.defaultWindowFamilies");

        /// <summary>Roots scanned when auto-loading families from disk. Default: none.</summary>
        public static string[] FamilySearchPaths => GetStringList("families.familySearchPaths");

        #endregion

        #region Typed settings — user / firm profiles

        /// <summary>Display name of the person using the bridge (injected into agent prompts). Default: empty.</summary>
        public static string UserName => GetString("user.name");

        /// <summary>Fallback firm-profile id used when the profile index has no defaultProfile. Default: empty.</summary>
        public static string DefaultFirmProfileId => GetString("firmProfiles.defaultProfileId");

        /// <summary>
        /// Firm-name → sheet-pattern-id mapping for sheet pattern detection.
        /// Default: empty — firm names are personal/client data and never ship in source.
        /// </summary>
        public static Dictionary<string, string> FirmSheetPrefixes => GetStringMap("sheetPatterns.firmPrefixes");

        /// <summary>
        /// Pattern-id → pattern definition objects extracted from real firm projects.
        /// Default: empty — extracted patterns describe client projects and never ship in source.
        /// </summary>
        public static JObject ExtractedSheetPatterns => GetJObject("sheetPatterns.extractedPatterns");

        /// <summary>
        /// Per-pattern-id overrides merged over the built-in generic pattern rules
        /// (use to attach firm names / licensed-professional info to a pattern).
        /// </summary>
        public static JObject SheetPatternRuleOverrides => GetJObject("sheetPatterns.patternRuleOverrides");

        #endregion
    }
}
