SET NOCOUNT ON;
GO

IF OBJECT_ID('dbo.SetupGenerations', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.SetupGenerations
    (
        GenerationId NVARCHAR(100) NOT NULL,
        Version NVARCHAR(100) NULL,
        Revision INT NULL,
        EnvironmentId NVARCHAR(100) NOT NULL,
        Status NVARCHAR(50) NOT NULL,
        StartedAt DATETIME2(3) NOT NULL,
        FinishedAt DATETIME2(3) NULL,
        LastFilePath NVARCHAR(1000) NULL,
        LastFileGeneratedAt DATETIME2(3) NULL,
        ValidityMinutes INT NOT NULL
            CONSTRAINT DF_SetupGenerations_ValidityMinutes DEFAULT (5),
        CreatedBy NVARCHAR(200) NULL,
        ExecutionId NVARCHAR(100) NULL,
        CONSTRAINT PK_SetupGenerations PRIMARY KEY CLUSTERED (GenerationId),
        CONSTRAINT FK_SetupGenerations_Execution
            FOREIGN KEY (ExecutionId) REFERENCES dbo.PipelineExecutions (ExecutionId)
    );
END;
GO

IF OBJECT_ID('dbo.SetupGenerationFiles', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.SetupGenerationFiles
    (
        Id BIGINT IDENTITY(1,1) NOT NULL,
        GenerationId NVARCHAR(100) NOT NULL,
        ProjectId NVARCHAR(100) NOT NULL,
        FilePath NVARCHAR(1000) NOT NULL,
        GeneratedAt DATETIME2(3) NOT NULL,
        Success BIT NOT NULL,
        CONSTRAINT PK_SetupGenerationFiles PRIMARY KEY CLUSTERED (Id),
        CONSTRAINT FK_SetupGenerationFiles_Generation
            FOREIGN KEY (GenerationId) REFERENCES dbo.SetupGenerations (GenerationId),
        CONSTRAINT FK_SetupGenerationFiles_Project
            FOREIGN KEY (ProjectId) REFERENCES dbo.Projects (Id)
    );
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_SetupGenerations_Environment_Status_StartedAt'
      AND object_id = OBJECT_ID('dbo.SetupGenerations')
)
BEGIN
    CREATE INDEX IX_SetupGenerations_Environment_Status_StartedAt
        ON dbo.SetupGenerations (EnvironmentId, Status, StartedAt DESC);
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_SetupGenerations_Status_FinishedAt'
      AND object_id = OBJECT_ID('dbo.SetupGenerations')
)
BEGIN
    CREATE INDEX IX_SetupGenerations_Status_FinishedAt
        ON dbo.SetupGenerations (Status, FinishedAt DESC);
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_SetupGenerationFiles_GenerationId'
      AND object_id = OBJECT_ID('dbo.SetupGenerationFiles')
)
BEGIN
    CREATE INDEX IX_SetupGenerationFiles_GenerationId
        ON dbo.SetupGenerationFiles (GenerationId, GeneratedAt DESC);
END;
GO
