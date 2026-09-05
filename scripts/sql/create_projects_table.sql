/*
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : create_projects_table.sql
Descrição : Cria a tabela de projetos do OuroBuild.
--------------------------------------------------------------------
*/

IF OBJECT_ID(
    N'dbo.Projects',
    N'U'
) IS NULL
BEGIN
    CREATE TABLE dbo.Projects
    (
        Id NVARCHAR(100) NOT NULL,

        Name NVARCHAR(200) NOT NULL,

        Description NVARCHAR(MAX) NOT NULL,

        Type NVARCHAR(50) NOT NULL,

        SolutionPath NVARCHAR(1000) NULL,

        ProjectPath NVARCHAR(1000) NULL,

        CompilationTarget NVARCHAR(50) NOT NULL,

        CompilationEngine NVARCHAR(50) NOT NULL,

        PublishPath NVARCHAR(1000) NOT NULL,

        PublishProfile NVARCHAR(200) NULL,

        AipPath NVARCHAR(1000) NOT NULL,

        VisualStudioSetupPath NVARCHAR(1000) NULL,

        OutputMsi NVARCHAR(1000) NOT NULL,

        NetworkPath NVARCHAR(1000) NOT NULL,

        Configuration NVARCHAR(100) NOT NULL,

        Platform NVARCHAR(100) NOT NULL,

        Enabled BIT NOT NULL,

        CONSTRAINT PK_Projects
            PRIMARY KEY (Id)
    );

    PRINT 'Tabela dbo.Projects criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela dbo.Projects já existe.';
END;