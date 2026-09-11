/*
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : 005_create_cleanup_rules.sql
Descrição : Cria a tabela de regras de limpeza específicas
            por projeto.

Importante:
    - Não altera a tabela dbo.Projects.
    - Não recria projetos existentes.
    - Não insere registros em dbo.Projects.
    - As regras específicas ficam vinculadas ao ProjectId.
--------------------------------------------------------------------
*/

SET NOCOUNT ON;
SET XACT_ABORT ON;

BEGIN TRY

    BEGIN TRANSACTION;

    /*
    ----------------------------------------------------------------
    Cria a tabela somente se ainda não existir.
    ----------------------------------------------------------------
    */

    IF OBJECT_ID(
        N'dbo.CleanupRules',
        N'U'
    ) IS NULL
    BEGIN

        CREATE TABLE dbo.CleanupRules
        (
            Id BIGINT IDENTITY(1, 1)
                NOT NULL,

            ProjectId NVARCHAR(100)
                NULL,

            Target NVARCHAR(30)
                NOT NULL,

            Pattern NVARCHAR(1000)
                NOT NULL,

            Action NVARCHAR(30)
                NOT NULL,

            Recursive BIT
                NOT NULL
                CONSTRAINT DF_CleanupRules_Recursive
                DEFAULT (1),

            Description NVARCHAR(2000)
                NULL,

            Priority INT
                NOT NULL
                CONSTRAINT DF_CleanupRules_Priority
                DEFAULT (100),

            Enabled BIT
                NOT NULL
                CONSTRAINT DF_CleanupRules_Enabled
                DEFAULT (1),

            CONSTRAINT PK_CleanupRules
                PRIMARY KEY CLUSTERED (Id),

            CONSTRAINT FK_CleanupRules_Projects
                FOREIGN KEY (ProjectId)
                REFERENCES dbo.Projects(Id)
                ON DELETE CASCADE,

            CONSTRAINT CK_CleanupRules_Target
                CHECK (
                    Target IN (
                        N'file',
                        N'directory'
                    )
                ),

            CONSTRAINT CK_CleanupRules_Action
                CHECK (
                    Action IN (
                        N'remove',
                        N'preserve'
                    )
                )
        );

    END;

    /*
    ----------------------------------------------------------------
    Índice principal para consulta das regras.
    ----------------------------------------------------------------
    */

    IF NOT EXISTS
    (
        SELECT 1
        FROM sys.indexes
        WHERE
            object_id = OBJECT_ID(
                N'dbo.CleanupRules'
            )
            AND name = N'IX_CleanupRules_Project'
    )
    BEGIN

        CREATE INDEX IX_CleanupRules_Project
            ON dbo.CleanupRules
            (
                ProjectId,
                Enabled,
                Priority,
                Id
            );

    END;

    /*
    ----------------------------------------------------------------
    Regras globais.
    
    ProjectId = NULL significa regra global.
    ----------------------------------------------------------------
    */

    IF NOT EXISTS
    (
        SELECT 1
        FROM dbo.CleanupRules
        WHERE
            ProjectId IS NULL
            AND Target = N'file'
            AND Pattern = N'*'
            AND Action = N'remove'
    )
    BEGIN

        INSERT INTO dbo.CleanupRules
        (
            ProjectId,
            Target,
            Pattern,
            Action,
            Recursive,
            Description,
            Priority,
            Enabled
        )
        VALUES
        (
            NULL,
            N'file',
            N'*',
            N'remove',
            1,
            N'Remove todos os arquivos do resultado do Build. Arquivos necessários devem ser preservados através de uma regra específica.',
            100,
            1
        );

    END;

    /*
    ----------------------------------------------------------------
    Exceção global para DLLs.
    ----------------------------------------------------------------
    */

    IF NOT EXISTS
    (
        SELECT 1
        FROM dbo.CleanupRules
        WHERE
            ProjectId IS NULL
            AND Target = N'file'
            AND Pattern = N'*.dll'
            AND Action = N'preserve'
    )
    BEGIN

        INSERT INTO dbo.CleanupRules
        (
            ProjectId,
            Target,
            Pattern,
            Action,
            Recursive,
            Description,
            Priority,
            Enabled
        )
        VALUES
        (
            NULL,
            N'file',
            N'*.dll',
            N'preserve',
            1,
            N'Preserva todas as DLLs necessárias em tempo de execução.',
            110,
            1
        );

    END;

    /*
    ----------------------------------------------------------------
    Regra global para diretórios.
    ----------------------------------------------------------------
    */

    IF NOT EXISTS
    (
        SELECT 1
        FROM dbo.CleanupRules
        WHERE
            ProjectId IS NULL
            AND Target = N'directory'
            AND Pattern = N'*'
            AND Action = N'remove'
    )
    BEGIN

        INSERT INTO dbo.CleanupRules
        (
            ProjectId,
            Target,
            Pattern,
            Action,
            Recursive,
            Description,
            Priority,
            Enabled
        )
        VALUES
        (
            NULL,
            N'directory',
            N'*',
            N'remove',
            1,
            N'Remove todos os diretórios do resultado do Build. Diretórios necessários devem ser preservados através de uma regra específica.',
            100,
            1
        );

    END;

    /*
    ----------------------------------------------------------------
    Exceções atuais do LinkPagamento.
    
    Somente insere se o projeto já existir.
    Nunca cria o projeto.
    ----------------------------------------------------------------
    */

    IF EXISTS
    (
        SELECT 1
        FROM dbo.Projects
        WHERE Id = N'linkpagamento'
    )
    BEGIN

        IF NOT EXISTS
        (
            SELECT 1
            FROM dbo.CleanupRules
            WHERE
                ProjectId = N'linkpagamento'
                AND Target = N'file'
                AND Pattern =
                    N'OuroNetWinServiceLinkPagamento.exe'
                AND Action = N'preserve'
        )
        BEGIN

            INSERT INTO dbo.CleanupRules
            (
                ProjectId,
                Target,
                Pattern,
                Action,
                Recursive,
                Description,
                Priority,
                Enabled
            )
            VALUES
            (
                N'linkpagamento',
                N'file',
                N'OuroNetWinServiceLinkPagamento.exe',
                N'preserve',
                1,
                N'Preserva o executável principal do Windows Service LinkPagamento.',
                200,
                1
            );

        END;

        IF NOT EXISTS
        (
            SELECT 1
            FROM dbo.CleanupRules
            WHERE
                ProjectId = N'linkpagamento'
                AND Target = N'file'
                AND Pattern =
                    N'OuroNetWinServiceLinkPagamento.exe.config'
                AND Action = N'preserve'
        )
        BEGIN

            INSERT INTO dbo.CleanupRules
            (
                ProjectId,
                Target,
                Pattern,
                Action,
                Recursive,
                Description,
                Priority,
                Enabled
            )
            VALUES
            (
                N'linkpagamento',
                N'file',
                N'OuroNetWinServiceLinkPagamento.exe.config',
                N'preserve',
                1,
                N'Preserva o arquivo de configuração principal do Windows Service LinkPagamento.',
                200,
                1
            );

        END;

    END;

    /*
    ----------------------------------------------------------------
    Exceções atuais do WCF Movimento.
    ----------------------------------------------------------------
    */

    IF EXISTS
    (
        SELECT 1
        FROM dbo.Projects
        WHERE Id = N'wcfmovimento'
    )
    BEGIN

        INSERT INTO dbo.CleanupRules
        (
            ProjectId,
            Target,
            Pattern,
            Action,
            Recursive,
            Description,
            Priority,
            Enabled
        )
        SELECT
            N'wcfmovimento',
            N'file',
            source.Pattern,
            N'preserve',
            1,
            source.Description,
            200,
            1
        FROM
        (
            VALUES
            (
                N'connectionStrings.config',
                N'Preserva o arquivo de conexão do WCF Movimento.'
            ),
            (
                N'custom.configuration.server.config',
                N'Preserva a configuração customizada do servidor do WCF Movimento.'
            ),
            (
                N'Movimento.svc',
                N'Preserva o serviço Movimento.'
            ),
            (
                N'packages.config',
                N'Preserva a configuração de pacotes do WCF Movimento.'
            ),
            (
                N'Web.config',
                N'Preserva a configuração web do WCF Movimento.'
            )
        ) AS source
        (
            Pattern,
            Description
        )
        WHERE NOT EXISTS
        (
            SELECT 1
            FROM dbo.CleanupRules existing
            WHERE
                existing.ProjectId =
                    N'wcfmovimento'
                AND existing.Target =
                    N'file'
                AND existing.Pattern =
                    source.Pattern
                AND existing.Action =
                    N'preserve'
        );

        IF NOT EXISTS
        (
            SELECT 1
            FROM dbo.CleanupRules
            WHERE
                ProjectId = N'wcfmovimento'
                AND Target = N'directory'
                AND Pattern = N'Xml'
                AND Action = N'preserve'
        )
        BEGIN

            INSERT INTO dbo.CleanupRules
            (
                ProjectId,
                Target,
                Pattern,
                Action,
                Recursive,
                Description,
                Priority,
                Enabled
            )
            VALUES
            (
                N'wcfmovimento',
                N'directory',
                N'Xml',
                N'preserve',
                1,
                N'Preserva a pasta XML utilizada pelo WCF Movimento.',
                200,
                1
            );

        END;

    END;

    /*
    ----------------------------------------------------------------
    Exceções atuais do WCF Cadastro.
    ----------------------------------------------------------------
    */

    IF EXISTS
    (
        SELECT 1
        FROM dbo.Projects
        WHERE Id = N'wcfcadastro'
    )
    BEGIN

        INSERT INTO dbo.CleanupRules
        (
            ProjectId,
            Target,
            Pattern,
            Action,
            Recursive,
            Description,
            Priority,
            Enabled
        )
        SELECT
            N'wcfcadastro',
            N'file',
            source.Pattern,
            N'preserve',
            1,
            source.Description,
            200,
            1
        FROM
        (
            VALUES
            (
                N'connectionStrings.config',
                N'Preserva o arquivo de conexão do WCF Cadastro.'
            ),
            (
                N'custom.configuration.server.config',
                N'Preserva a configuração customizada do servidor do WCF Cadastro.'
            ),
            (
                N'Cadastro.svc',
                N'Preserva o serviço Cadastro.'
            ),
            (
                N'CadastroWS.asmx',
                N'Preserva o serviço web CadastroWS.'
            ),
            (
                N'packages.config',
                N'Preserva a configuração de pacotes do WCF Cadastro.'
            ),
            (
                N'Web.config',
                N'Preserva a configuração web do WCF Cadastro.'
            )
        ) AS source
        (
            Pattern,
            Description
        )
        WHERE NOT EXISTS
        (
            SELECT 1
            FROM dbo.CleanupRules existing
            WHERE
                existing.ProjectId =
                    N'wcfcadastro'
                AND existing.Target =
                    N'file'
                AND existing.Pattern =
                    source.Pattern
                AND existing.Action =
                    N'preserve'
        );

        INSERT INTO dbo.CleanupRules
        (
            ProjectId,
            Target,
            Pattern,
            Action,
            Recursive,
            Description,
            Priority,
            Enabled
        )
        SELECT
            N'wcfcadastro',
            N'directory',
            source.Pattern,
            N'remove',
            1,
            source.Description,
            300,
            1
        FROM
        (
            VALUES
            (
                N'x86',
                N'Remove o diretório nativo x86 do WCF Cadastro.'
            ),
            (
                N'x64',
                N'Remove o diretório nativo x64 do WCF Cadastro.'
            ),
            (
                N'arm64',
                N'Remove o diretório nativo arm64 do WCF Cadastro.'
            )
        ) AS source
        (
            Pattern,
            Description
        )
        WHERE NOT EXISTS
        (
            SELECT 1
            FROM dbo.CleanupRules existing
            WHERE
                existing.ProjectId =
                    N'wcfcadastro'
                AND existing.Target =
                    N'directory'
                AND existing.Pattern =
                    source.Pattern
                AND existing.Action =
                    N'remove'
        );

    END;

    /*
    ----------------------------------------------------------------
    Exceções atuais do WCF Financeiro.
    ----------------------------------------------------------------
    */

    IF EXISTS
    (
        SELECT 1
        FROM dbo.Projects
        WHERE Id = N'wcffinanceiro'
    )
    BEGIN

        INSERT INTO dbo.CleanupRules
        (
            ProjectId,
            Target,
            Pattern,
            Action,
            Recursive,
            Description,
            Priority,
            Enabled
        )
        SELECT
            N'wcffinanceiro',
            N'file',
            source.Pattern,
            N'preserve',
            1,
            source.Description,
            200,
            1
        FROM
        (
            VALUES
            (
                N'connectionStrings.config',
                N'Preserva o arquivo de conexão do WCF Financeiro.'
            ),
            (
                N'custom.configuration.server.config',
                N'Preserva a configuração customizada do servidor do WCF Financeiro.'
            ),
            (
                N'Financial.svc',
                N'Preserva o serviço Financeiro.'
            ),
            (
                N'packages.config',
                N'Preserva a configuração de pacotes do WCF Financeiro.'
            ),
            (
                N'Web.config',
                N'Preserva a configuração web do WCF Financeiro.'
            )
        ) AS source
        (
            Pattern,
            Description
        )
        WHERE NOT EXISTS
        (
            SELECT 1
            FROM dbo.CleanupRules existing
            WHERE
                existing.ProjectId =
                    N'wcffinanceiro'
                AND existing.Target =
                    N'file'
                AND existing.Pattern =
                    source.Pattern
                AND existing.Action =
                    N'preserve'
        );

        INSERT INTO dbo.CleanupRules
        (
            ProjectId,
            Target,
            Pattern,
            Action,
            Recursive,
            Description,
            Priority,
            Enabled
        )
        SELECT
            N'wcffinanceiro',
            N'directory',
            source.Pattern,
            N'remove',
            1,
            source.Description,
            300,
            1
        FROM
        (
            VALUES
            (
                N'x86',
                N'Remove o diretório nativo x86 do WCF Financeiro.'
            ),
            (
                N'x64',
                N'Remove o diretório nativo x64 do WCF Financeiro.'
            ),
            (
                N'arm64',
                N'Remove o diretório nativo arm64 do WCF Financeiro.'
            )
        ) AS source
        (
            Pattern,
            Description
        )
        WHERE NOT EXISTS
        (
            SELECT 1
            FROM dbo.CleanupRules existing
            WHERE
                existing.ProjectId =
                    N'wcffinanceiro'
                AND existing.Target =
                    N'directory'
                AND existing.Pattern =
                    source.Pattern
                AND existing.Action =
                    N'remove'
        );

    END;

    /*
    ----------------------------------------------------------------
    Exceções atuais do OuroNet.
    
    Mantemos o comportamento atualmente existente no provider.
    ----------------------------------------------------------------
    */

    IF EXISTS
    (
        SELECT 1
        FROM dbo.Projects
        WHERE Id = N'ouronet'
    )
    BEGIN

        INSERT INTO dbo.CleanupRules
        (
            ProjectId,
            Target,
            Pattern,
            Action,
            Recursive,
            Description,
            Priority,
            Enabled
        )
        SELECT
            N'ouronet',
            N'file',
            source.Pattern,
            N'preserve',
            1,
            source.Description,
            200,
            1
        FROM
        (
            VALUES
            (
                N'OuroNetApp.exe',
                N'Preserva o executável principal do OuroNet.'
            ),
            (
                N'OuroNetApp.exe.config',
                N'Preserva o arquivo de configuração principal do OuroNet.'
            )
        ) AS source
        (
            Pattern,
            Description
        )
        WHERE NOT EXISTS
        (
            SELECT 1
            FROM dbo.CleanupRules existing
            WHERE
                existing.ProjectId =
                    N'ouronet'
                AND existing.Target =
                    N'file'
                AND existing.Pattern =
                    source.Pattern
                AND existing.Action =
                    N'preserve'
        );

        INSERT INTO dbo.CleanupRules
        (
            ProjectId,
            Target,
            Pattern,
            Action,
            Recursive,
            Description,
            Priority,
            Enabled
        )
        SELECT
            N'ouronet',
            N'directory',
            source.Pattern,
            N'preserve',
            1,
            source.Description,
            200,
            1
        FROM
        (
            VALUES
            (
                N'x86',
                N'Preserva o diretório nativo x86 do OuroNet.'
            ),
            (
                N'x64',
                N'Preserva o diretório nativo x64 do OuroNet.'
            ),
            (
                N'arm64',
                N'Preserva o diretório nativo arm64 do OuroNet.'
            )
        ) AS source
        (
            Pattern,
            Description
        )
        WHERE NOT EXISTS
        (
            SELECT 1
            FROM dbo.CleanupRules existing
            WHERE
                existing.ProjectId =
                    N'ouronet'
                AND existing.Target =
                    N'directory'
                AND existing.Pattern =
                    source.Pattern
                AND existing.Action =
                    N'preserve'
        );

    END;

    COMMIT TRANSACTION;

END TRY
BEGIN CATCH

    IF @@TRANCOUNT > 0
    BEGIN
        ROLLBACK TRANSACTION;
    END;

    THROW;

END CATCH;