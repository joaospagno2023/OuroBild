/*
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : authorization.sql
Descrição : Estrutura de perfis e permissões do OuroBuild.
--------------------------------------------------------------------
*/

SET NOCOUNT ON;
GO

/*
--------------------------------------------------------------------
1. Tabela de perfis
--------------------------------------------------------------------
*/

IF OBJECT_ID('dbo.Roles', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Roles
    (
        Id INT IDENTITY(1,1) NOT NULL,
        Name NVARCHAR(100) NOT NULL,
        Description NVARCHAR(255) NULL,
        IsActive BIT NOT NULL
            CONSTRAINT DF_Roles_IsActive DEFAULT (1),
        CreatedAt DATETIME2 NOT NULL
            CONSTRAINT DF_Roles_CreatedAt
            DEFAULT (SYSUTCDATETIME()),

        CONSTRAINT PK_Roles
            PRIMARY KEY (Id),

        CONSTRAINT UQ_Roles_Name
            UNIQUE (Name)
    );
END;
GO

/*
--------------------------------------------------------------------
2. Tabela de permissões
--------------------------------------------------------------------
*/

IF OBJECT_ID('dbo.Permissions', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Permissions
    (
        Id INT IDENTITY(1,1) NOT NULL,
        [Key] NVARCHAR(100) NOT NULL,
        Name NVARCHAR(100) NOT NULL,
        Description NVARCHAR(255) NULL,
        IsActive BIT NOT NULL
            CONSTRAINT DF_Permissions_IsActive DEFAULT (1),
        CreatedAt DATETIME2 NOT NULL
            CONSTRAINT DF_Permissions_CreatedAt
            DEFAULT (SYSUTCDATETIME()),

        CONSTRAINT PK_Permissions
            PRIMARY KEY (Id),

        CONSTRAINT UQ_Permissions_Key
            UNIQUE ([Key])
    );
END;
GO

/*
--------------------------------------------------------------------
3. Relação usuário x perfil
--------------------------------------------------------------------
*/

IF OBJECT_ID('dbo.UserRoles', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.UserRoles
    (
        UserId INT NOT NULL,
        RoleId INT NOT NULL,
        CreatedAt DATETIME2 NOT NULL
            CONSTRAINT DF_UserRoles_CreatedAt
            DEFAULT (SYSUTCDATETIME()),

        CONSTRAINT PK_UserRoles
            PRIMARY KEY (UserId, RoleId),

        CONSTRAINT FK_UserRoles_User
            FOREIGN KEY (UserId)
            REFERENCES dbo.Users(Id),

        CONSTRAINT FK_UserRoles_Role
            FOREIGN KEY (RoleId)
            REFERENCES dbo.Roles(Id)
    );
END;
GO

/*
--------------------------------------------------------------------
4. Relação perfil x permissão
--------------------------------------------------------------------
*/

IF OBJECT_ID('dbo.RolePermissions', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.RolePermissions
    (
        RoleId INT NOT NULL,
        PermissionId INT NOT NULL,
        CreatedAt DATETIME2 NOT NULL
            CONSTRAINT DF_RolePermissions_CreatedAt
            DEFAULT (SYSUTCDATETIME()),

        CONSTRAINT PK_RolePermissions
            PRIMARY KEY (RoleId, PermissionId),

        CONSTRAINT FK_RolePermissions_Role
            FOREIGN KEY (RoleId)
            REFERENCES dbo.Roles(Id),

        CONSTRAINT FK_RolePermissions_Permission
            FOREIGN KEY (PermissionId)
            REFERENCES dbo.Permissions(Id)
    );
END;
GO

/*
--------------------------------------------------------------------
5. Perfis padrão
--------------------------------------------------------------------
*/

IF NOT EXISTS
(
    SELECT 1
    FROM dbo.Roles
    WHERE Name = N'Administrador'
)
BEGIN
    INSERT INTO dbo.Roles
    (
        Name,
        Description,
        IsActive
    )
    VALUES
    (
        N'Administrador',
        N'Acesso completo ao OuroBuild.',
        1
    );
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM dbo.Roles
    WHERE Name = N'Operador'
)
BEGIN
    INSERT INTO dbo.Roles
    (
        Name,
        Description,
        IsActive
    )
    VALUES
    (
        N'Operador',
        N'Executa Build e Setup e consulta histórico e logs.',
        1
    );
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM dbo.Roles
    WHERE Name = N'Consulta'
)
BEGIN
    INSERT INTO dbo.Roles
    (
        Name,
        Description,
        IsActive
    )
    VALUES
    (
        N'Consulta',
        N'Permite somente consulta de informações.',
        1
    );
END;
GO

/*
--------------------------------------------------------------------
6. Permissões padrão
--------------------------------------------------------------------
*/

IF NOT EXISTS
(
    SELECT 1
    FROM dbo.Permissions
    WHERE [Key] = N'dashboard.view'
)
BEGIN
    INSERT INTO dbo.Permissions
    (
        [Key],
        Name,
        Description,
        IsActive
    )
    VALUES
    (
        N'dashboard.view',
        N'Visualizar Dashboard',
        N'Permite visualizar o Dashboard.',
        1
    );
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM dbo.Permissions
    WHERE [Key] = N'setup.execute'
)
BEGIN
    INSERT INTO dbo.Permissions
    (
        [Key],
        Name,
        Description,
        IsActive
    )
    VALUES
    (
        N'setup.execute',
        N'Executar Setup',
        N'Permite executar a geração de Setup.',
        1
    );
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM dbo.Permissions
    WHERE [Key] = N'build.execute'
)
BEGIN
    INSERT INTO dbo.Permissions
    (
        [Key],
        Name,
        Description,
        IsActive
    )
    VALUES
    (
        N'build.execute',
        N'Executar Build',
        N'Permite executar Build.',
        1
    );
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM dbo.Permissions
    WHERE [Key] = N'history.view'
)
BEGIN
    INSERT INTO dbo.Permissions
    (
        [Key],
        Name,
        Description,
        IsActive
    )
    VALUES
    (
        N'history.view',
        N'Visualizar Histórico',
        N'Permite consultar o histórico das execuções.',
        1
    );
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM dbo.Permissions
    WHERE [Key] = N'logs.view'
)
BEGIN
    INSERT INTO dbo.Permissions
    (
        [Key],
        Name,
        Description,
        IsActive
    )
    VALUES
    (
        N'logs.view',
        N'Visualizar Logs',
        N'Permite consultar logs.',
        1
    );
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM dbo.Permissions
    WHERE [Key] = N'users.manage'
)
BEGIN
    INSERT INTO dbo.Permissions
    (
        [Key],
        Name,
        Description,
        IsActive
    )
    VALUES
    (
        N'users.manage',
        N'Administrar Usuários',
        N'Permite criar, editar, ativar e desativar usuários.',
        1
    );
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM dbo.Permissions
    WHERE [Key] = N'administration.view'
)
BEGIN
    INSERT INTO dbo.Permissions
    (
        [Key],
        Name,
        Description,
        IsActive
    )
    VALUES
    (
        N'administration.view',
        N'Visualizar Administração',
        N'Permite acessar a área de administração.',
        1
    );
END;
GO

/*
--------------------------------------------------------------------
7. Administrador
--------------------------------------------------------------------
*/

INSERT INTO dbo.RolePermissions
(
    RoleId,
    PermissionId
)
SELECT
    r.Id,
    p.Id
FROM dbo.Roles r
CROSS JOIN dbo.Permissions p
WHERE r.Name = N'Administrador'
  AND NOT EXISTS
  (
      SELECT 1
      FROM dbo.RolePermissions rp
      WHERE rp.RoleId = r.Id
        AND rp.PermissionId = p.Id
  );
GO

/*
--------------------------------------------------------------------
8. Operador
--------------------------------------------------------------------
*/

INSERT INTO dbo.RolePermissions
(
    RoleId,
    PermissionId
)
SELECT
    r.Id,
    p.Id
FROM dbo.Roles r
INNER JOIN dbo.Permissions p
    ON p.[Key] IN
    (
        N'dashboard.view',
        N'setup.execute',
        N'build.execute',
        N'history.view',
        N'logs.view'
    )
WHERE r.Name = N'Operador'
  AND NOT EXISTS
  (
      SELECT 1
      FROM dbo.RolePermissions rp
      WHERE rp.RoleId = r.Id
        AND rp.PermissionId = p.Id
  );
GO

/*
--------------------------------------------------------------------
9. Consulta
--------------------------------------------------------------------
*/

INSERT INTO dbo.RolePermissions
(
    RoleId,
    PermissionId
)
SELECT
    r.Id,
    p.Id
FROM dbo.Roles r
INNER JOIN dbo.Permissions p
    ON p.[Key] IN
    (
        N'dashboard.view',
        N'history.view',
        N'logs.view'
    )
WHERE r.Name = N'Consulta'
  AND NOT EXISTS
  (
      SELECT 1
      FROM dbo.RolePermissions rp
      WHERE rp.RoleId = r.Id
        AND rp.PermissionId = p.Id
  );
GO

/*
--------------------------------------------------------------------
10. Atribuir Administrador ao usuário joaospagnol
--------------------------------------------------------------------
*/

INSERT INTO dbo.UserRoles
(
    UserId,
    RoleId
)
SELECT
    u.Id,
    r.Id
FROM dbo.Users u
CROSS JOIN dbo.Roles r
WHERE u.Username = N'joaospagnol'
  AND r.Name = N'Administrador'
  AND NOT EXISTS
  (
      SELECT 1
      FROM dbo.UserRoles ur
      WHERE ur.UserId = u.Id
        AND ur.RoleId = r.Id
  );
GO

/*
--------------------------------------------------------------------
11. Validação
--------------------------------------------------------------------
*/

SELECT
    Id,
    Name,
    Description,
    IsActive,
    CreatedAt
FROM dbo.Roles
ORDER BY Id;
GO

SELECT
    Id,
    [Key],
    Name,
    Description,
    IsActive,
    CreatedAt
FROM dbo.Permissions
ORDER BY Id;
GO

SELECT
    u.Id AS UserId,
    u.Username,
    r.Id AS RoleId,
    r.Name AS RoleName
FROM dbo.UserRoles ur
INNER JOIN dbo.Users u
    ON u.Id = ur.UserId
INNER JOIN dbo.Roles r
    ON r.Id = ur.RoleId
ORDER BY
    u.Username,
    r.Name;
GO

SELECT
    r.Name AS RoleName,
    p.[Key] AS PermissionKey,
    p.Name AS PermissionName
FROM dbo.RolePermissions rp
INNER JOIN dbo.Roles r
    ON r.Id = rp.RoleId
INNER JOIN dbo.Permissions p
    ON p.Id = rp.PermissionId
ORDER BY
    r.Name,
    p.[Key];
GO