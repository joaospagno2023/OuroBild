/*
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : 004_add_setup_network_root_path.sql
Descrição : Adiciona o caminho raiz de rede às configurações de Setup.
--------------------------------------------------------------------
*/

SET NOCOUNT ON;
SET XACT_ABORT ON;

BEGIN TRANSACTION;

IF OBJECT_ID(
    N'dbo.ApplicationConfiguration',
    N'U'
) IS NULL
BEGIN
    THROW 50001,
        'A tabela dbo.ApplicationConfiguration não existe.',
        1;
END;

IF COL_LENGTH(
    'dbo.ApplicationConfiguration',
    'SetupNetworkRootPath'
) IS NULL
BEGIN
    ALTER TABLE dbo.ApplicationConfiguration
    ADD SetupNetworkRootPath NVARCHAR(2000) NULL;
END;

UPDATE dbo.ApplicationConfiguration
SET SetupNetworkRootPath =
    N'\\vm-srvfile01\Fontes\Application\OuroNet\Teste'
WHERE SetupNetworkRootPath IS NULL
   OR LTRIM(RTRIM(SetupNetworkRootPath)) = N'';

ALTER TABLE dbo.ApplicationConfiguration
ALTER COLUMN SetupNetworkRootPath NVARCHAR(2000) NOT NULL;

COMMIT TRANSACTION;
GO

/*
--------------------------------------------------------------------
Consulta de validação
--------------------------------------------------------------------
*/

SELECT
    Id,
    SetupNetworkRootPath
FROM dbo.ApplicationConfiguration;
GO