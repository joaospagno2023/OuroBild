/*
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : 005_create_setup_publication.sql
Descrição : Estrutura de persistência das publicações em lote
            de Setups e respectivos eventos.
--------------------------------------------------------------------
*/

SET NOCOUNT ON;
GO

IF OBJECT_ID('dbo.SetupPublicationBatches', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.SetupPublicationBatches
    (
        Id BIGINT IDENTITY(1,1) NOT NULL,
        BatchId NVARCHAR(64) NOT NULL,
        Version NVARCHAR(50) NOT NULL,
        Revision INT NOT NULL,
        SourcePath NVARCHAR(1000) NOT NULL,
        DestinationPath NVARCHAR(2000) NULL,
        Status NVARCHAR(30) NOT NULL,
        StartedAt DATETIME2(3) NOT NULL,
        FinishedAt DATETIME2(3) NULL,
        ElapsedSeconds DECIMAL(18,3) NULL,
        TotalSetups INT NOT NULL,
        CompletedSetups INT NOT NULL,
        FailedSetups INT NOT NULL,
        Message NVARCHAR(MAX) NULL,

        CONSTRAINT PK_SetupPublicationBatches
            PRIMARY KEY CLUSTERED (Id),

        CONSTRAINT UQ_SetupPublicationBatches_BatchId
            UNIQUE (BatchId)
    );
END;
GO

IF OBJECT_ID('dbo.SetupPublicationLogs', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.SetupPublicationLogs
    (
        Id BIGINT IDENTITY(1,1) NOT NULL,
        BatchId NVARCHAR(64) NOT NULL,
        Timestamp DATETIME2(3) NOT NULL,
        Level NVARCHAR(20) NOT NULL,
        EventType NVARCHAR(50) NOT NULL,
        ProjectId NVARCHAR(100) NULL,
        ExecutionId NVARCHAR(100) NULL,
        Message NVARCHAR(MAX) NOT NULL,
        Details NVARCHAR(MAX) NULL,

        CONSTRAINT PK_SetupPublicationLogs
            PRIMARY KEY CLUSTERED (Id),

        CONSTRAINT FK_SetupPublicationLogs_Batch
            FOREIGN KEY (BatchId)
            REFERENCES dbo.SetupPublicationBatches (BatchId)
            ON DELETE CASCADE
    );
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'IX_SetupPublicationLogs_BatchId'
      AND object_id = OBJECT_ID('dbo.SetupPublicationLogs')
)
BEGIN
    CREATE INDEX IX_SetupPublicationLogs_BatchId
        ON dbo.SetupPublicationLogs (BatchId, Timestamp, Id);
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'IX_SetupPublicationBatches_StartedAt'
      AND object_id = OBJECT_ID('dbo.SetupPublicationBatches')
)
BEGIN
    CREATE INDEX IX_SetupPublicationBatches_StartedAt
        ON dbo.SetupPublicationBatches (StartedAt DESC);
END;
GO

SELECT
    t.name AS TableName,
    c.name AS ColumnName,
    ty.name AS DataType,
    c.max_length AS MaxLength,
    c.is_nullable AS IsNullable
FROM sys.tables t
INNER JOIN sys.columns c
    ON c.object_id = t.object_id
INNER JOIN sys.types ty
    ON ty.user_type_id = c.user_type_id
WHERE t.name IN (
    'SetupPublicationBatches',
    'SetupPublicationLogs'
)
ORDER BY
    t.name,
    c.column_id;
GO
