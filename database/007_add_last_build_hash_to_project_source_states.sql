/*
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : 007_add_last_build_hash_to_project_source_states.sql
Descrição : Adiciona o hash do último BUILD bem-sucedido, separado
             do hash "da última verificação" (SourceHash), usado
             para decidir com segurança se Restore/Build podem ser
             pulados quando nada mudou desde o último build que
             realmente deu certo.
--------------------------------------------------------------------
*/

SET NOCOUNT ON;
SET XACT_ABORT ON;

BEGIN TRY
    BEGIN TRANSACTION;

    IF NOT EXISTS (
        SELECT 1
        FROM sys.columns
        WHERE object_id = OBJECT_ID(N'dbo.ProjectSourceStates')
          AND name = 'LastBuildHash'
    )
    BEGIN
        ALTER TABLE dbo.ProjectSourceStates
        ADD LastBuildHash NVARCHAR(64) NULL;
    END;

    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;
    THROW;
END CATCH;
GO
