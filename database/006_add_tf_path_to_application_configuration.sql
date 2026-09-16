/*
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : 006_add_tf_path_to_application_configuration.sql
Descrição : Adiciona o caminho configurável do TF.exe (TFVC).
--------------------------------------------------------------------
*/

SET NOCOUNT ON;
GO

IF COL_LENGTH(N'dbo.ApplicationConfiguration', N'TfPath') IS NULL
BEGIN
    ALTER TABLE dbo.ApplicationConfiguration
    ADD TfPath NVARCHAR(1000) NOT NULL
        CONSTRAINT DF_ApplicationConfiguration_TfPath
        DEFAULT (N'C:\Program Files\Microsoft Visual Studio\18\Professional\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\TF.exe');

    PRINT 'Coluna dbo.ApplicationConfiguration.TfPath criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Coluna dbo.ApplicationConfiguration.TfPath já existe.';
END;
GO

SELECT Id, TfPath
FROM dbo.ApplicationConfiguration
WHERE Id = 1;
GO
