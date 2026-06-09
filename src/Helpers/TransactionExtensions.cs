using System;
using Autodesk.Revit.DB;

namespace RevitMCPBridge
{
    /// <summary>
    /// Commit that surfaces rollback instead of swallowing it.
    ///
    /// Revit rolls a transaction back when an error-severity failure is
    /// posted (the WarningSwallower preprocessor only deletes warnings).
    /// A bare Commit() then returns TransactionStatus.RolledBack, and a
    /// caller that ignores the status reports success with the IDs of
    /// elements that no longer exist. CommitAndCheck throws instead, so the
    /// method's existing catch path returns a real error to the caller.
    /// </summary>
    public static class TransactionExtensions
    {
        public static void CommitAndCheck(this Transaction trans)
        {
            var status = trans.Commit();
            if (status != TransactionStatus.Committed)
            {
                throw new InvalidOperationException(
                    $"Transaction '{trans.GetName()}' did not commit (status: {status}). " +
                    "Revit rolled it back — likely an error-severity failure was posted. " +
                    "No model changes from this operation were kept.");
            }
        }

        public static void CommitAndCheck(this SubTransaction trans)
        {
            var status = trans.Commit();
            if (status != TransactionStatus.Committed)
            {
                throw new InvalidOperationException(
                    $"SubTransaction did not commit (status: {status}). " +
                    "Revit rolled it back — no changes from this step were kept.");
            }
        }
    }
}
