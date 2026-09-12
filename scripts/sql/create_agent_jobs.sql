IF OBJECT_ID('dbo.AgentJobs', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.AgentJobs
    (
        Id BIGINT IDENTITY(1, 1) NOT NULL,

        AgentId INT NULL,

        JobType VARCHAR(50) NOT NULL,

        Status VARCHAR(20) NOT NULL,

        ProjectId VARCHAR(100) NULL,

        EnvironmentId VARCHAR(100) NULL,

        Parameters NVARCHAR(MAX) NULL,

        CreatedAt DATETIME2(3) NOT NULL
            CONSTRAINT DF_AgentJobs_CreatedAt
            DEFAULT SYSUTCDATETIME(),

        StartedAt DATETIME2(3) NULL,

        FinishedAt DATETIME2(3) NULL,

        ErrorMessage NVARCHAR(MAX) NULL,

        CONSTRAINT PK_AgentJobs
            PRIMARY KEY CLUSTERED (Id),

        CONSTRAINT FK_AgentJobs_Agents
            FOREIGN KEY (AgentId)
            REFERENCES dbo.Agents(Id),

        CONSTRAINT CK_AgentJobs_Status
            CHECK
            (
                Status IN
                (
                    'PENDING',
                    'RUNNING',
                    'COMPLETED',
                    'FAILED',
                    'CANCELLED'
                )
            )
    );

    CREATE INDEX IX_AgentJobs_Status_CreatedAt
        ON dbo.AgentJobs
        (
            Status,
            CreatedAt
        );

    CREATE INDEX IX_AgentJobs_AgentId
        ON dbo.AgentJobs
        (
            AgentId
        );
END;
GO