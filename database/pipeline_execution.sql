/*
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_execution.sql
Descrição : Estrutura de persistência das execuções, steps,
            processos e logs da Pipeline.
--------------------------------------------------------------------
*/

SET NOCOUNT ON;
GO

IF OBJECT_ID('dbo.PipelineExecutions', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.PipelineExecutions
    (
        Id BIGINT IDENTITY(1,1) NOT NULL,
        ExecutionId NVARCHAR(100) NOT NULL,
        ProjectId NVARCHAR(100) NOT NULL,
        EnvironmentId NVARCHAR(100) NULL,
        Status NVARCHAR(30) NOT NULL,
        StartedAt DATETIME2(3) NOT NULL,
        FinishedAt DATETIME2(3) NULL,
        DurationSeconds DECIMAL(18,3) NULL,
        Success BIT NULL,
        FailedStep NVARCHAR(200) NULL,
        Message NVARCHAR(MAX) NULL,

        CONSTRAINT PK_PipelineExecutions
            PRIMARY KEY CLUSTERED (Id),

        CONSTRAINT UQ_PipelineExecutions_ExecutionId
            UNIQUE (ExecutionId),

        CONSTRAINT FK_PipelineExecutions_Project
            FOREIGN KEY (ProjectId)
            REFERENCES dbo.Projects (Id),

        CONSTRAINT FK_PipelineExecutions_Environment
            FOREIGN KEY (EnvironmentId)
            REFERENCES dbo.Environments (Id)
    );
END;
GO

IF OBJECT_ID('dbo.PipelineExecutionSteps', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.PipelineExecutionSteps
    (
        Id BIGINT IDENTITY(1,1) NOT NULL,
        ExecutionId NVARCHAR(100) NOT NULL,
        StepName NVARCHAR(200) NOT NULL,
        StepOrder INT NOT NULL,
        Status NVARCHAR(30) NOT NULL,
        StartedAt DATETIME2(3) NULL,
        FinishedAt DATETIME2(3) NULL,
        DurationSeconds DECIMAL(18,3) NULL,
        Message NVARCHAR(MAX) NULL,

        CONSTRAINT PK_PipelineExecutionSteps
            PRIMARY KEY CLUSTERED (Id),

        CONSTRAINT FK_PipelineExecutionSteps_Execution
            FOREIGN KEY (ExecutionId)
            REFERENCES dbo.PipelineExecutions (ExecutionId)
            ON DELETE CASCADE
    );
END;
GO

IF OBJECT_ID('dbo.PipelineExecutionProcesses', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.PipelineExecutionProcesses
    (
        Id BIGINT IDENTITY(1,1) NOT NULL,
        ExecutionId NVARCHAR(100) NOT NULL,
        StepId BIGINT NULL,
        Executable NVARCHAR(1000) NOT NULL,
        WorkingDirectory NVARCHAR(1000) NULL,
        CommandLine NVARCHAR(MAX) NULL,
        Arguments NVARCHAR(MAX) NULL,
        ExitCode INT NULL,
        Status NVARCHAR(30) NOT NULL,
        StartedAt DATETIME2(3) NOT NULL,
        FinishedAt DATETIME2(3) NULL,
        DurationSeconds DECIMAL(18,3) NULL,
        Stdout NVARCHAR(MAX) NULL,
        Stderr NVARCHAR(MAX) NULL,

        CONSTRAINT PK_PipelineExecutionProcesses
            PRIMARY KEY CLUSTERED (Id),

        CONSTRAINT FK_PipelineExecutionProcesses_Execution
            FOREIGN KEY (ExecutionId)
            REFERENCES dbo.PipelineExecutions (ExecutionId)
            ON DELETE CASCADE,

        CONSTRAINT FK_PipelineExecutionProcesses_Step
            FOREIGN KEY (StepId)
            REFERENCES dbo.PipelineExecutionSteps (Id)
    );
END;
GO

IF OBJECT_ID('dbo.PipelineExecutionLogs', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.PipelineExecutionLogs
    (
        Id BIGINT IDENTITY(1,1) NOT NULL,
        ExecutionId NVARCHAR(100) NOT NULL,
        StepId BIGINT NULL,
        ProcessId BIGINT NULL,
        Timestamp DATETIME2(3) NOT NULL,
        Level NVARCHAR(20) NOT NULL,
        Source NVARCHAR(200) NULL,
        Message NVARCHAR(MAX) NOT NULL,
        Details NVARCHAR(MAX) NULL,

        CONSTRAINT PK_PipelineExecutionLogs
            PRIMARY KEY CLUSTERED (Id),

        CONSTRAINT FK_PipelineExecutionLogs_Execution
            FOREIGN KEY (ExecutionId)
            REFERENCES dbo.PipelineExecutions (ExecutionId)
            ON DELETE CASCADE,

        CONSTRAINT FK_PipelineExecutionLogs_Step
            FOREIGN KEY (StepId)
            REFERENCES dbo.PipelineExecutionSteps (Id),

        CONSTRAINT FK_PipelineExecutionLogs_Process
            FOREIGN KEY (ProcessId)
            REFERENCES dbo.PipelineExecutionProcesses (Id)
    );
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_PipelineExecutions_ProjectId'
      AND object_id = OBJECT_ID('dbo.PipelineExecutions')
)
BEGIN
    CREATE INDEX IX_PipelineExecutions_ProjectId
        ON dbo.PipelineExecutions (ProjectId);
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_PipelineExecutions_EnvironmentId'
      AND object_id = OBJECT_ID('dbo.PipelineExecutions')
)
BEGIN
    CREATE INDEX IX_PipelineExecutions_EnvironmentId
        ON dbo.PipelineExecutions (EnvironmentId);
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_PipelineExecutions_StartedAt'
      AND object_id = OBJECT_ID('dbo.PipelineExecutions')
)
BEGIN
    CREATE INDEX IX_PipelineExecutions_StartedAt
        ON dbo.PipelineExecutions (StartedAt DESC);
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_PipelineExecutions_Status'
      AND object_id = OBJECT_ID('dbo.PipelineExecutions')
)
BEGIN
    CREATE INDEX IX_PipelineExecutions_Status
        ON dbo.PipelineExecutions (Status);
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_PipelineExecutionSteps_ExecutionId'
      AND object_id = OBJECT_ID('dbo.PipelineExecutionSteps')
)
BEGIN
    CREATE INDEX IX_PipelineExecutionSteps_ExecutionId
        ON dbo.PipelineExecutionSteps (ExecutionId, StepOrder);
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_PipelineExecutionProcesses_ExecutionId'
      AND object_id = OBJECT_ID('dbo.PipelineExecutionProcesses')
)
BEGIN
    CREATE INDEX IX_PipelineExecutionProcesses_ExecutionId
        ON dbo.PipelineExecutionProcesses (ExecutionId);
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_PipelineExecutionLogs_ExecutionId'
      AND object_id = OBJECT_ID('dbo.PipelineExecutionLogs')
)
BEGIN
    CREATE INDEX IX_PipelineExecutionLogs_ExecutionId
        ON dbo.PipelineExecutionLogs (ExecutionId, Timestamp);
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
    'PipelineExecutions',
    'PipelineExecutionSteps',
    'PipelineExecutionProcesses',
    'PipelineExecutionLogs'
)
ORDER BY
    t.name,
    c.column_id;
GO
