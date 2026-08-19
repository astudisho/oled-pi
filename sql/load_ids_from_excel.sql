/*
    load_ids_from_excel.sql

    Loads ID values (and optionally other columns) from an Excel workbook
    and inserts them as new rows into a SQL Server table, using OPENROWSET
    against the Excel ACE OLEDB provider.

    ------------------------------------------------------------------
    PREREQUISITES (one-time, per SQL Server instance)
    ------------------------------------------------------------------
    1. Install the "Microsoft Access Database Engine" (ACE OLEDB provider)
       matching your SQL Server's bitness (64-bit for a 64-bit instance):
       https://www.microsoft.com/en-us/download/details.aspx?id=54920

    2. Enable Ad Hoc Distributed Queries and allow in-process for the
       provider (requires sysadmin):

       EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
       EXEC sp_configure 'Ad Hoc Distributed Queries', 1; RECONFIGURE;
       EXEC sp_configure 'show advanced options', 0; RECONFIGURE;

       EXEC master.dbo.sp_MSset_oledb_prop N'Microsoft.ACE.OLEDB.16.0', N'AllowInProcess', 1;
       EXEC master.dbo.sp_MSset_oledb_prop N'Microsoft.ACE.OLEDB.16.0', N'DynamicParameters', 1;

    3. The .xlsx file must be readable by the SQL Server service account
       from the path used below (a UNC/network path is usually easiest).

    ------------------------------------------------------------------
    CONFIGURATION - edit these before running
    ------------------------------------------------------------------
*/

DECLARE @ExcelPath   NVARCHAR(260) = N'\\server\share\ids.xlsx';  -- path to the workbook
DECLARE @SheetName   NVARCHAR(128) = N'Sheet1$';                  -- sheet name, keep the trailing $
DECLARE @TargetTable NVARCHAR(128) = N'dbo.MyTargetTable';        -- destination table
DECLARE @TargetCol   NVARCHAR(128) = N'Id';                       -- destination column for the ID

-- ------------------------------------------------------------------
-- Preview: what will be read from Excel (run this block first to check)
-- ------------------------------------------------------------------
SELECT *
FROM OPENROWSET(
    'Microsoft.ACE.OLEDB.16.0',
    'Excel 12.0 Xlsx;HDR=YES;IMEX=1;Database=\\server\share\ids.xlsx',
    'SELECT * FROM [Sheet1$]'
);

-- ------------------------------------------------------------------
-- Insert: load the Id column from Excel into the target table
-- NOTE: OPENROWSET does not accept variables for the connection
--       string/query, so update the literals below to match the
--       @ExcelPath / @SheetName / @TargetCol values you set above,
--       or build/execute the statement dynamically with sp_executesql.
-- ------------------------------------------------------------------
INSERT INTO dbo.MyTargetTable (Id)
SELECT Id
FROM OPENROWSET(
    'Microsoft.ACE.OLEDB.16.0',
    'Excel 12.0 Xlsx;HDR=YES;IMEX=1;Database=\\server\share\ids.xlsx',
    'SELECT * FROM [Sheet1$]'
) AS src;

-- ------------------------------------------------------------------
-- Dynamic version (uses the @ExcelPath / @SheetName / @TargetTable /
-- @TargetCol variables above, so you only edit the DECLAREs)
-- ------------------------------------------------------------------
DECLARE @sql NVARCHAR(MAX) = N'
INSERT INTO ' + @TargetTable + N' (' + @TargetCol + N')
SELECT Id
FROM OPENROWSET(
    ''Microsoft.ACE.OLEDB.16.0'',
    ''Excel 12.0 Xlsx;HDR=YES;IMEX=1;Database=' + @ExcelPath + N''',
    ''SELECT * FROM [' + @SheetName + N']''
) AS src;';

EXEC sp_executesql @sql;
