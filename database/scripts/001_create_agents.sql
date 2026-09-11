/*
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : 001_create_agents.sql
Descrição : Cria a tabela de Agents do OuroBuild.
--------------------------------------------------------------------
*/

IF OBJECT_ID(N'dbo.Agents', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Agents
    (
        Id INT IDENTITY(1,1) NOT NULL,
        Name NVARCHAR(100) NOT NULL,
        MachineName NVARCHAR(255) NOT NULL,
        UserName NVARCHAR(255) NOT NULL,
        Version NVARCHAR(50) NOT NULL,
        Status NVARCHAR(30) NOT NULL
            CONSTRAINT DF_Agents_Status DEFAULT ('OFFLINE'),
        LastHeartbeat DATETIME2(3) NULL,
        CreatedAt DATETIME2(3) NOT NULL
            CONSTRAINT DF_Agents_CreatedAt DEFAULT (SYSUTCDATETIME()),
        UpdatedAt DATETIME2(3) NOT NULL
            CONSTRAINT DF_Agents_UpdatedAt DEFAULT (SYSUTCDATETIME()),

        CONSTRAINT PK_Agents
            PRIMARY KEY CLUSTERED (Id),

        CONSTRAINT UQ_Agents_MachineUser
            UNIQUE (MachineName, UserName)
    );
END;
GO
