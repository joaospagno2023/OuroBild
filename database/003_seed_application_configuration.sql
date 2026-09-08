/*
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : 003_seed_application_configuration.sql
Descrição :
    Popula a configuração inicial do OuroBuild em
    dbo.ApplicationConfiguration.

    IMPORTANTE:
    - O registro canônico é Id = 1.
    - Este script NÃO grava a configuração do banco de dados.
      A conexão continua em config/settings.json.
    - Preencha somente o JWT_SECRET antes de executar.
--------------------------------------------------------------------
*/

SET NOCOUNT ON;
SET XACT_ABORT ON;

BEGIN TRY

    BEGIN TRANSACTION;

    DECLARE @Id TINYINT = 1;

    DECLARE @ApplicationName NVARCHAR(200) = N'OuroBuild';
    DECLARE @Version NVARCHAR(50) = N'1.0.0';
    DECLARE @LogLevel NVARCHAR(20) = N'INFO';

    DECLARE @BasePath NVARCHAR(1000) =
        N'C:\Custom\OuroWeb';

    DECLARE @InstallerPath NVARCHAR(1000) =
        N'C:\Custom\OuroWeb\Installer';

    DECLARE @PublishPath NVARCHAR(1000) =
        N'C:\Custom\OuroWeb\Publish';

    DECLARE @MsBuildPath NVARCHAR(1000) =
        N'C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe';

    DECLARE @AdvancedInstallerPath NVARCHAR(1000) =
        N'C:\Program Files (x86)\Caphyon\Advanced Installer 23.7\bin\x86\AdvancedInstaller.com';

    DECLARE @RobocopyPath NVARCHAR(1000) =
        N'C:\Windows\System32\robocopy.exe';

    DECLARE @SetupEngine NVARCHAR(50) =
        N'advanced_installer';

    DECLARE @SetupOutputRoot NVARCHAR(1000) =
        N'C:\Setups';

    DECLARE @SetupAipRoot NVARCHAR(2000) =
        N'C:\DvpLocal\WorkSpaceTFS\Transferencia de Arquivo\TransferenciaDeArquivos\Setups\Installers\Projects';

    DECLARE @SetupExcluirPastaWork BIT = 0;

    DECLARE @LoggingEnabled BIT = 1;

    DECLARE @LoggingPath NVARCHAR(1000) =
        N'C:\Custom\ourobuild\app\logs';

    DECLARE @LoggingLevel NVARCHAR(20) =
        N'DEBUG';

    DECLARE @StorageWorkspacePath NVARCHAR(1000) =
        N'C:\Custom\OuroBuild';

    /*
    ----------------------------------------------------------------
    SEGURANÇA
    ----------------------------------------------------------------
    NÃO coloque o segredo real neste arquivo se ele for versionado.

    Preencha @JwtSecret manualmente antes de executar este script.
    ----------------------------------------------------------------
    */
    DECLARE @JwtSecret NVARCHAR(4000) =
        N'COLOQUE_AQUI_O_JWT_SECRET_ATUAL';

    DECLARE @JwtAlgorithm NVARCHAR(50) =
        N'HS256';

    DECLARE @TokenExpirationMinutes INT =
        180;

    IF @JwtSecret = N'COLOQUE_AQUI_O_JWT_SECRET_ATUAL'
    BEGIN
        THROW 50001,
            'Defina o JWT Secret antes de executar a migracao.',
            1;
    END;

    IF EXISTS
    (
        SELECT 1
        FROM dbo.ApplicationConfiguration
        WHERE Id = @Id
    )
    BEGIN

        UPDATE dbo.ApplicationConfiguration
        SET
            ApplicationName = @ApplicationName,
            Version = @Version,
            LogLevel = @LogLevel,
            BasePath = @BasePath,
            InstallerPath = @InstallerPath,
            PublishPath = @PublishPath,
            MsBuildPath = @MsBuildPath,
            AdvancedInstallerPath = @AdvancedInstallerPath,
            RobocopyPath = @RobocopyPath,
            SetupEngine = @SetupEngine,
            SetupOutputRoot = @SetupOutputRoot,
            SetupAipRoot = @SetupAipRoot,
            SetupExcluirPastaWork = @SetupExcluirPastaWork,
            LoggingEnabled = @LoggingEnabled,
            LoggingPath = @LoggingPath,
            LoggingLevel = @LoggingLevel,
            StorageWorkspacePath = @StorageWorkspacePath,
            JwtSecret = @JwtSecret,
            JwtAlgorithm = @JwtAlgorithm,
            TokenExpirationMinutes = @TokenExpirationMinutes,
            UpdatedAt = SYSUTCDATETIME()
        WHERE Id = @Id;

    END
    ELSE
    BEGIN

        SET IDENTITY_INSERT dbo.ApplicationConfiguration ON;

        INSERT INTO dbo.ApplicationConfiguration
        (
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
            JwtSecret,
            JwtAlgorithm,
            TokenExpirationMinutes,
            CreatedAt,
            UpdatedAt
        )
        VALUES
        (
            @Id,
            @ApplicationName,
            @Version,
            @LogLevel,
            @BasePath,
            @InstallerPath,
            @PublishPath,
            @MsBuildPath,
            @AdvancedInstallerPath,
            @RobocopyPath,
            @SetupEngine,
            @SetupOutputRoot,
            @SetupAipRoot,
            @SetupExcluirPastaWork,
            @LoggingEnabled,
            @LoggingPath,
            @LoggingLevel,
            @StorageWorkspacePath,
            @JwtSecret,
            @JwtAlgorithm,
            @TokenExpirationMinutes,
            SYSUTCDATETIME(),
            SYSUTCDATETIME()
        );

        SET IDENTITY_INSERT dbo.ApplicationConfiguration OFF;

    END;

    COMMIT TRANSACTION;

    SELECT
        Id,
        ApplicationName,
        Version,
        LogLevel,
        SetupEngine,
        SetupOutputRoot,
        SetupExcluirPastaWork,
        LoggingEnabled,
        LoggingLevel,
        JwtAlgorithm,
        TokenExpirationMinutes,
        CreatedAt,
        UpdatedAt
    FROM dbo.ApplicationConfiguration
    WHERE Id = @Id;

END TRY
BEGIN CATCH

    IF XACT_STATE() <> 0
        ROLLBACK TRANSACTION;

    BEGIN TRY
        SET IDENTITY_INSERT dbo.ApplicationConfiguration OFF;
    END TRY
    BEGIN CATCH
    END CATCH;

    THROW;

END CATCH;
