/*
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : 001_create_users.sql
Descrição : Cria a tabela de usuários do OuroBuild.
--------------------------------------------------------------------
*/

IF OBJECT_ID(
    N'dbo.Users',
    N'U'
) IS NULL
BEGIN

    CREATE TABLE dbo.Users
    (
        Id INT IDENTITY(1,1) NOT NULL,

        Username NVARCHAR(100) NOT NULL,

        PasswordHash NVARCHAR(500) NOT NULL,

        DisplayName NVARCHAR(150) NOT NULL,

        Email NVARCHAR(254) NULL,

        IsActive BIT NOT NULL
            CONSTRAINT DF_Users_IsActive
            DEFAULT (1),

        CreatedAt DATETIME2(0) NOT NULL
            CONSTRAINT DF_Users_CreatedAt
            DEFAULT (SYSUTCDATETIME()),

        LastLoginAt DATETIME2(0) NULL,

        CONSTRAINT PK_Users
            PRIMARY KEY (Id),

        CONSTRAINT UQ_Users_Username
            UNIQUE (Username)
    );

END;
GO