/*
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : 002_create_application_configuration.sql
Descrição :
    Cria a tabela de configuração operacional do OuroBuild.

    A tabela armazena todas as configurações da aplicação,
    exceto as configurações de conexão com o banco de dados.

    A conexão com o banco continuará sendo obtida inicialmente
    através do settings.json.
--------------------------------------------------------------------
*/

SET NOCOUNT ON;
GO

IF OBJECT_ID(
    N'dbo.ApplicationConfiguration',
    N'U'
) IS NULL
BEGIN

    CREATE TABLE dbo.ApplicationConfiguration
    (
        Id INT IDENTITY(1,1) NOT NULL,

        /*
        ------------------------------------------------------------
        Aplicação
        ------------------------------------------------------------
        */

        ApplicationName NVARCHAR(200) NOT NULL,

        Version NVARCHAR(50) NOT NULL,

        LogLevel NVARCHAR(20) NOT NULL,

        /*
        ------------------------------------------------------------
        Caminhos
        ------------------------------------------------------------
        */

        BasePath NVARCHAR(1000) NOT NULL,

        InstallerPath NVARCHAR(1000) NOT NULL,

        PublishPath NVARCHAR(1000) NOT NULL,

        /*
        ------------------------------------------------------------
        Build Tools
        ------------------------------------------------------------
        */

        MsBuildPath NVARCHAR(1000) NOT NULL,

        AdvancedInstallerPath NVARCHAR(1000) NOT NULL,

        RobocopyPath NVARCHAR(1000) NOT NULL,

        /*
        ------------------------------------------------------------
        Setup
        ------------------------------------------------------------
        */

        SetupEngine NVARCHAR(50) NOT NULL,

        SetupOutputRoot NVARCHAR(1000) NOT NULL,

        SetupAipRoot NVARCHAR(2000) NOT NULL,

        SetupExcluirPastaWork BIT NOT NULL
            CONSTRAINT DF_ApplicationConfiguration_SetupExcluirPastaWork
            DEFAULT (0),

        /*
        ------------------------------------------------------------
        Logging
        ------------------------------------------------------------
        */

        LoggingEnabled BIT NOT NULL
            CONSTRAINT DF_ApplicationConfiguration_LoggingEnabled
            DEFAULT (1),

        LoggingPath NVARCHAR(1000) NOT NULL,

        LoggingLevel NVARCHAR(20) NOT NULL,

        /*
        ------------------------------------------------------------
        Storage
        ------------------------------------------------------------
        */

        StorageWorkspacePath NVARCHAR(1000) NOT NULL,

        /*
        ------------------------------------------------------------
        Segurança
        ------------------------------------------------------------
        */

        JwtSecret NVARCHAR(500) NOT NULL,

        JwtAlgorithm NVARCHAR(50) NOT NULL,

        TokenExpirationMinutes INT NOT NULL,

        /*
        ------------------------------------------------------------
        Auditoria
        ------------------------------------------------------------
        */

        CreatedAt DATETIME2(3) NOT NULL
            CONSTRAINT DF_ApplicationConfiguration_CreatedAt
            DEFAULT (SYSUTCDATETIME()),

        UpdatedAt DATETIME2(3) NOT NULL
            CONSTRAINT DF_ApplicationConfiguration_UpdatedAt
            DEFAULT (SYSUTCDATETIME()),

        /*
        ------------------------------------------------------------
        Constraints
        ------------------------------------------------------------
        */

        CONSTRAINT PK_ApplicationConfiguration
            PRIMARY KEY CLUSTERED (Id),

        CONSTRAINT UQ_ApplicationConfiguration_Singleton
            UNIQUE (Id)
    );

    PRINT 'Tabela dbo.ApplicationConfiguration criada com sucesso.';

END
ELSE
BEGIN

    PRINT 'Tabela dbo.ApplicationConfiguration já existe.';

END;
GO

/*
--------------------------------------------------------------------
Garante que exista apenas uma configuração principal.

A tabela será utilizada inicialmente como Singleton.
--------------------------------------------------------------------
*/

IF NOT EXISTS
(
    SELECT 1
    FROM dbo.ApplicationConfiguration
)
BEGIN

    INSERT INTO dbo.ApplicationConfiguration
    (
        ApplicationName,
        Version,
        LogLevel,

        BasePath,
        InstallerPath,
        PublishPath,

        MsBuildPath,
        AdvancedInstallerPath,
        RobocopyPath,

        SetupEngine,
        SetupOutputRoot,
        SetupAipRoot,
        SetupExcluirPastaWork,

        LoggingEnabled,
        LoggingPath,
        LoggingLevel,

        StorageWorkspacePath,

        JwtSecret,
        JwtAlgorithm,
        TokenExpirationMinutes
    )
    VALUES
    (
        N'OuroBuild 1.0 teste',
        N'1.0.0',
        N'INFO',

        N'C:\Custom\OuroWeb',
        N'C:\Custom\OuroWeb\Installer',
        N'C:\Custom\OuroWeb\Publish',

        N'C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe',
        N'C:\Program Files (x86)\Caphyon\Advanced Installer 21.9\bin\x86\AdvancedInstaller.com',
        N'C:\Windows\System32\robocopy.exe',

        N'advanced_installer',
        N'C:\Setups',
        N'C:\DvpLocal\WorkSpaceTFS\Transferencia de Arquivo\TransferenciaDeArquivos\Setups\Installers\Projects',
        0,

        1,
        N'C:\Custom\ourobuild\app\logs',
        N'DEBUG',

        N'C:\Custom\ourobuild',

        N'COLOQUE_AQUI_O_JWT_SECRET_ATUAL',
        N'HS256',
        180
    );

    PRINT 'Configuração inicial inserida em dbo.ApplicationConfiguration.';

END
ELSE
BEGIN

    PRINT 'Configuração inicial já existe. Nenhum registro foi inserido.';

END;
GO

/*
--------------------------------------------------------------------
Consulta de validação
--------------------------------------------------------------------
*/

SELECT
    Id,
    ApplicationName,
    Version,
    LogLevel,
    BasePath,
    InstallerPath,
    PublishPath,
    MsBuildPath,
    AdvancedInstallerPath,
    RobocopyPath,
    SetupEngine,
    SetupOutputRoot,
    SetupAipRoot,
    SetupExcluirPastaWork,
    LoggingEnabled,
    LoggingPath,
    LoggingLevel,
    StorageWorkspacePath,
    JwtAlgorithm,
    TokenExpirationMinutes,
    CreatedAt,
    UpdatedAt
FROM dbo.ApplicationConfiguration;
GO