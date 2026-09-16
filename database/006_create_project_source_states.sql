/*
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : 006_create_project_source_states.sql
Descrição : Persiste o hash dos fontes e os marcos de Get Last/Build.
--------------------------------------------------------------------
*/

SET NOCOUNT ON;
SET XACT_ABORT ON;

BEGIN TRY
    BEGIN TRANSACTION;

    IF OBJECT_ID(N'dbo.ProjectSourceStates', N'U') IS NULL
    BEGIN
        CREATE TABLE dbo.ProjectSourceStates
        (
            Id BIGINT IDENTITY(1,1) NOT NULL,
            ProjectId NVARCHAR(100) NOT NULL,
            SourceHash NVARCHAR(64) NOT NULL,
            LastCheckedAt DATETIME2(3) NULL,
            LastGetLastAt DATETIME2(3) NULL,
            LastBuildAt DATETIME2(3) NULL,

            CONSTRAINT PK_ProjectSourceStates
                PRIMARY KEY CLUSTERED (Id),

            CONSTRAINT UQ_ProjectSourceStates_ProjectId
                UNIQUE (ProjectId),

            CONSTRAINT FK_ProjectSourceStates_Project
                FOREIGN KEY (ProjectId)
                REFERENCES dbo.Projects(Id)
                ON DELETE CASCADE
        );
    END;

    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;
    THROW;
END CATCH;
GO
