# bridge_config.json — RevitMCPBridge2026 machine/firm configuration

All machine-specific paths and firm-specific data live in `bridge_config.json`.
Nothing personal (drive layouts, client names, licensed-professional info) is
compiled into the DLL — if a key is missing, the bridge uses a neutral default
or returns a clear error telling you which key to set.

## Where the bridge looks for the file

1. `bridge_config.json` **next to the deployed `RevitMCPBridge2026.dll`**
   (e.g. `%APPDATA%\Autodesk\Revit\Addins\2026\bridge_config.json`)
2. `%APPDATA%\RevitMCPBridge\bridge_config.json`

First file found wins. The file is read once per Revit session and cached.
Start from `bridge_config.sample.json` — every key is optional.

## What happens with NO config file

- Logs, batch progress, and the capability system go to `%APPDATA%\RevitMCPBridge\…`
- The knowledge base is looked for in a `knowledge` folder next to the DLL
- Library/template/family methods that need a local path return an error
  naming the key to configure (they never probe your drives blindly)
- No firm sheet-numbering profiles are active; sheet pattern detection falls
  back to the generic industry patterns (`A`, `C`, `C-Zero`, `C-Institutional`, `D`)

## Keys

### `user`
| Key | Meaning | Default |
|---|---|---|
| `name` | Display name injected into the in-Revit agent's prompts ("the user is …") | empty (no name mentioned) |

### `paths`
| Key | Meaning | Default |
|---|---|---|
| `logDirectory` | Bridge log/progress files (`batch_text.log`, `batch_progress.json`) | `%APPDATA%\RevitMCPBridge\logs` |
| `capabilitySystemDirectory` | Self-expanding capability system data (tool specs, failure logs) | `%APPDATA%\RevitMCPBridge\capability_system` |
| `knowledgeDirectory` | Knowledge base root (firm profiles in `standards\firm-profiles`, extracted rules, agent knowledge files) | `knowledge` folder next to the DLL, else `%APPDATA%\RevitMCPBridge\knowledge` |
| `workflowsDirectory` | Workflow JSON templates | probed next to the DLL |
| `scriptsDirectory` | Automation scripts (e.g. `load_autodesk_family.py`) | probed next to the DLL |
| `templateSearchPaths` | Extra folders scanned for `.rte` project templates (list) | none (built-in Revit template folders are always scanned) |
| `firmTemplatesDirectory` | Where `saveAsTemplate` writes firm templates | empty — method asks you to configure it |
| `sharedParametersFile` | Default shared-parameters `.txt` for smart templates | empty — method asks you to configure it |
| `libraryRootDirectory` | Root of the indexed detail/family library (`library_index.json`) | empty — pass `libraryPath` per call or configure |
| `detailLibraryDirectory` | The "Revit Details" folder used by detail/batch-text methods | empty — pass `libraryPath` per call or configure |
| `detailLibrarySearchPaths` | Detail libraries searched by `findCompatibleDetails`, in preference order (list) | none |
| `libraryProfilePaths` | Detail Library window default profile (keys: `Details`, `Families`, `Legends`, `Schedules`) | empty paths |
| `fileSearchRoots` | Roots the agent's `search_files` tool may scan when no path is given (list) | none |

### `families`
| Key | Meaning | Default |
|---|---|---|
| `defaultDoorFamilies` | Candidate `.rfa` files loaded when a door is placed and none is loaded (list, in order) | none |
| `defaultWindowFamilies` | Same for windows | none |
| `familySearchPaths` | Roots scanned when auto-loading families from disk (list, in order) | none |

### `firmProfiles`
| Key | Meaning | Default |
|---|---|---|
| `defaultProfileId` | Fallback firm-profile id when `_profile-index.json` has no `defaultProfile` | empty |

### `sheetPatterns`
| Key | Meaning | Default |
|---|---|---|
| `firmPrefixes` | Map of firm name → sheet-pattern id, used by `detectSheetPattern` (e.g. `{ "Acme Architects": "ThreeDigitCompact" }`) | empty |
| `extractedPatterns` | Map of pattern id → full pattern spec extracted from your firm's real projects | empty |
| `patternRuleOverrides` | Per-id replacements for the built-in generic patterns (`A`, `C`, `C-Zero`, `C-Institutional`, `D`) — attach your firm names / licensed-professional info here | none |

Pattern ids are arbitrary strings; the ids `DotCategory`, `HyphenDecimal`,
`ThreeDigitCompact`, and `DisciplineDecimal` additionally get tuned
schedule-sheet placement in the smart sheet matcher.

## Security note

The named pipe (`RevitMCPBridge2026`) is created with an ACL that only allows
connections from the Windows user running Revit. If ACL creation fails on an
unusual environment, the bridge logs a warning and falls back to an
unauthenticated pipe — watch the log for "Pipe ACL" warnings.
