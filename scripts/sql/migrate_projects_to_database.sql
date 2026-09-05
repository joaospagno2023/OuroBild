/*
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : migrate_projects_to_database.sql
Descrição : Migra os projetos configurados no projects.json
            para a tabela dbo.Projects.
--------------------------------------------------------------------
*/

SET NOCOUNT ON;
SET XACT_ABORT ON;

BEGIN TRY

    BEGIN TRANSACTION;

    IF OBJECT_ID(
        N'dbo.Projects',
        N'U'
    ) IS NULL
    BEGIN
        THROW 50001,
            'A tabela dbo.Projects não existe.',
            1;
    END;

    /*
    ----------------------------------------------------------------
    Projeto: linkpagamento
    ----------------------------------------------------------------
    */

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.Projects
        WHERE Id = N'linkpagamento'
    )
    BEGIN
        INSERT INTO dbo.Projects
        (
            Id,
            Name,
            Description,
            Type,
            SolutionPath,
            ProjectPath,
            CompilationTarget,
            CompilationEngine,
            PublishPath,
            PublishProfile,
            AipPath,
            VisualStudioSetupPath,
            OutputMsi,
            NetworkPath,
            Configuration,
            Platform,
            Enabled
        )
        VALUES
        (
            N'linkpagamento',
            N'WinService LinkPagamento',
            N'Serviço responsável pelo LinkPagamento',
            N'client',
            NULL,
            N'02-Source\01-Client\OuroNet.Client.WinService.LinkPagamento\OuroNet.Client.WinService.LinkPagamento.csproj',
            N'solution',
            N'msbuild',
            N'bin\Release',
            N'',
            N'OuroNet.WinServiceLinkPagamento.aip',
            N'04-Setup\OuroNet.Client.WinServiceLinkPagamento.Setup\OuroNet.Client.WinServiceLinkPagamento.Setup.vdproj',
            N'OuroNet.Client.WinServiceLinkPagamento.Setup.msi',
            N'\\Servidor\Builds',
            N'Release',
            N'AnyCPU',
            1
        );
    END;

    /*
    ----------------------------------------------------------------
    Projeto: wcfcadastro
    ----------------------------------------------------------------
    */

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.Projects
        WHERE Id = N'wcfcadastro'
    )
    BEGIN
        INSERT INTO dbo.Projects
        (
            Id,
            Name,
            Description,
            Type,
            SolutionPath,
            ProjectPath,
            CompilationTarget,
            CompilationEngine,
            PublishPath,
            PublishProfile,
            AipPath,
            VisualStudioSetupPath,
            OutputMsi,
            NetworkPath,
            Configuration,
            Platform,
            Enabled
        )
        VALUES
        (
            N'wcfcadastro',
            N'Ouro Net Server Cadastro',
            N'Serviço responsável pelo Server de Cadastro',
            N'server',
            NULL,
            N'02-Source\02-Server\OuroNet.Server.WCF.Cadastre\OuroNet.Server.WCF.Cadastre.csproj',
            N'solution',
            N'msbuild',
            N'bin\app.publish',
            N'FolderProfile',
            N'OuroNet.Server.Cadastre.Setup.aip',
            N'',
            N'OuroNet.Server.Cadastre.Setup.msi',
            N'\\Servidor\Builds',
            N'Release',
            N'AnyCPU',
            1
        );
    END;

    /*
    ----------------------------------------------------------------
    Projeto: wcfmovimento
    ----------------------------------------------------------------
    */

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.Projects
        WHERE Id = N'wcfmovimento'
    )
    BEGIN
        INSERT INTO dbo.Projects
        (
            Id,
            Name,
            Description,
            Type,
            SolutionPath,
            ProjectPath,
            CompilationTarget,
            CompilationEngine,
            PublishPath,
            PublishProfile,
            AipPath,
            VisualStudioSetupPath,
            OutputMsi,
            NetworkPath,
            Configuration,
            Platform,
            Enabled
        )
        VALUES
        (
            N'wcfmovimento',
            N'Ouro Net Server Movimento',
            N'Serviço responsável pelo Server de Movimento',
            N'server',
            NULL,
            N'02-Source\02-Server\OuroNet.Server.WCF.Movement\OuroNet.Server.WCF.Movement.csproj',
            N'solution',
            N'msbuild',
            N'bin\app.publish',
            N'FolderProfile',
            N'OuroNet.Server.Movement.Setup.aip',
            N'',
            N'OuroNet.Server.Movement.Setup.msi',
            N'\\Servidor\Builds',
            N'Release',
            N'AnyCPU',
            1
        );
    END;

    /*
    ----------------------------------------------------------------
    Projeto: wcffinanceiro
    ----------------------------------------------------------------
    */

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.Projects
        WHERE Id = N'wcffinanceiro'
    )
    BEGIN
        INSERT INTO dbo.Projects
        (
            Id,
            Name,
            Description,
            Type,
            SolutionPath,
            ProjectPath,
            CompilationTarget,
            CompilationEngine,
            PublishPath,
            PublishProfile,
            AipPath,
            VisualStudioSetupPath,
            OutputMsi,
            NetworkPath,
            Configuration,
            Platform,
            Enabled
        )
        VALUES
        (
            N'wcffinanceiro',
            N'Ouro Net Server Financeiro',
            N'Serviço responsável pelo Server de Financeiro',
            N'server',
            NULL,
            N'02-Source\02-Server\OuroNet.Server.WCF.Financial\OuroNet.Server.WCF.Financial.csproj',
            N'solution',
            N'msbuild',
            N'bin\app.publish',
            N'FolderProfile',
            N'OuroNet.Server.Financial.Setup.aip',
            N'',
            N'OuroNet.Server.Financeiro.Setup.msi',
            N'\\Servidor\Builds',
            N'Release',
            N'AnyCPU',
            1
        );
    END;

    /*
    ----------------------------------------------------------------
    Projeto: ouronet
    ----------------------------------------------------------------
    */

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.Projects
        WHERE Id = N'ouronet'
    )
    BEGIN
        INSERT INTO dbo.Projects
        (
            Id,
            Name,
            Description,
            Type,
            SolutionPath,
            ProjectPath,
            CompilationTarget,
            CompilationEngine,
            PublishPath,
            PublishProfile,
            AipPath,
            VisualStudioSetupPath,
            OutputMsi,
            NetworkPath,
            Configuration,
            Platform,
            Enabled
        )
        VALUES
        (
            N'ouronet',
            N'Ouro Net App',
            N'Serviço responsável pelo Aplicativo OuroNet',
            N'client',
            NULL,
            N'02-Source\01-Client\OuroNet.Client.App\OuroNet.Client.App.csproj',
            N'solution',
            N'msbuild',
            N'bin\Release',
            N'FolderProfile',
            N'OuroNetApp.aip',
            N'',
            N'OuroNet.Client.App.Setup.msi',
            N'\\Servidor\Builds',
            N'Release',
            N'AnyCPU',
            1
        );
    END;

    /*
    ----------------------------------------------------------------
    Validação da quantidade esperada.
    ----------------------------------------------------------------
    */

    DECLARE @ProjectCount INT;

    SELECT
        @ProjectCount = COUNT(*)
    FROM dbo.Projects
    WHERE Id IN
    (
        N'linkpagamento',
        N'wcfcadastro',
        N'wcfmovimento',
        N'wcffinanceiro',
        N'ouronet'
    );

    IF @ProjectCount <> 5
    BEGIN
        THROW 50002,
            'A migração não encontrou os 5 projetos esperados.',
            1;
    END;

    COMMIT TRANSACTION;

    PRINT 'Migração dos projetos concluída com sucesso.';

END TRY
BEGIN CATCH

    IF @@TRANCOUNT > 0
    BEGIN
        ROLLBACK TRANSACTION;
    END;

    THROW;

END CATCH;

/*
--------------------------------------------------------------------
Conferência final
--------------------------------------------------------------------
*/

SELECT
    Id,
    Name,
    Type,
    ProjectPath,
    CompilationTarget,
    CompilationEngine,
    PublishPath,
    PublishProfile,
    AipPath,
    VisualStudioSetupPath,
    OutputMsi,
    NetworkPath,
    Configuration,
    Platform,
    Enabled
FROM dbo.Projects
WHERE Id IN
(
    N'linkpagamento',
    N'wcfcadastro',
    N'wcfmovimento',
    N'wcffinanceiro',
    N'ouronet'
)
ORDER BY Id;