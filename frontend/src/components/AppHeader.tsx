import {
  Bell,
  ChevronDown,
  KeyRound,
  LogOut,
  Menu,
  UserRound,
} from "lucide-react";

import {
  useState,
} from "react";

import {
  useNavigate,
} from "react-router-dom";

import {
  useAuth,
} from "../auth/AuthContext";


type AppHeaderProps = {
  onMenuClick: () => void;
};


function AppHeader({
  onMenuClick,
}: AppHeaderProps) {
  const {
    user,
    logout,
  } = useAuth();

  const navigate = useNavigate();

  const [userMenuOpen, setUserMenuOpen] =
    useState(false);

  function handleLogout(): void {
    setUserMenuOpen(false);
    logout();
  }

  function handleProfile(): void {
    setUserMenuOpen(false);

    navigate("/profile");
  }

  function handleChangePassword(): void {
    setUserMenuOpen(false);

    navigate("/profile");
  }

  const displayName =
    user?.display_name ||
    user?.username ||
    "Usuário";

  return (
    <header className="app-header">
      <button
        className="mobile-menu-button"
        type="button"
        onClick={onMenuClick}
        aria-label="Abrir menu"
      >
        <Menu size={21} />
      </button>

      <div className="header-title">
        <span>
          OuroBuild
        </span>

        <strong>
          Automação de Builds e Setups
        </strong>
      </div>

      <div className="header-actions">
        <button
          className="icon-button"
          type="button"
          aria-label="Notificações"
        >
          <Bell size={19} />

          <span className="notification-dot" />
        </button>

        <div
          className="user-menu"
          style={{
            position:
              "relative",
          }}
        >
          <button
            type="button"
            onClick={() =>
              setUserMenuOpen(
                (value) => !value,
              )
            }
            aria-expanded={
              userMenuOpen
            }
            aria-haspopup="menu"
            style={{
              display:
                "flex",
              alignItems:
                "center",
              gap:
                "9px",
              padding:
                0,
              border:
                0,
              background:
                "transparent",
              cursor:
                "pointer",
              color:
                "inherit",
            }}
          >
            <div className="user-avatar">
              {displayName
                .substring(0, 2)
                .toUpperCase()}
            </div>

            <div className="user-info">
              <strong>
                {displayName}
              </strong>

              <span>
                {user?.username}
              </span>
            </div>

            <ChevronDown
              size={17}
              style={{
                transform:
                  userMenuOpen
                    ? "rotate(180deg)"
                    : "rotate(0deg)",
                transition:
                  "transform 0.18s ease",
              }}
            />
          </button>

          {userMenuOpen && (
            <div
              role="menu"
              style={{
                position:
                  "absolute",
                top:
                  "calc(100% + 10px)",
                right:
                  0,
                width:
                  "230px",
                padding:
                  "6px",
                border:
                  "1px solid #e2e8f0",
                borderRadius:
                  "10px",
                background:
                  "#ffffff",
                boxShadow:
                  "0 14px 30px rgba(15, 23, 42, 0.12)",
                zIndex:
                  100,
              }}
            >
              <div
                style={{
                  padding:
                    "10px 12px",
                  borderBottom:
                    "1px solid #f1f5f9",
                  marginBottom:
                    "4px",
                }}
              >
                <strong
                  style={{
                    display:
                      "block",
                    color:
                      "#0f172a",
                    fontSize:
                      "12px",
                  }}
                >
                  {displayName}
                </strong>

                <span
                  style={{
                    display:
                      "block",
                    marginTop:
                      "2px",
                    color:
                      "#64748b",
                    fontSize:
                      "10px",
                  }}
                >
                  {user?.username}
                </span>
              </div>

              <button
                type="button"
                role="menuitem"
                onClick={
                  handleProfile
                }
                style={{
                  width:
                    "100%",
                  display:
                    "flex",
                  alignItems:
                    "center",
                  gap:
                    "10px",
                  padding:
                    "9px 10px",
                  border:
                    0,
                  borderRadius:
                    "7px",
                  background:
                    "transparent",
                  color:
                    "#334155",
                  cursor:
                    "pointer",
                  textAlign:
                    "left",
                  fontSize:
                    "12px",
                }}
              >
                <UserRound
                  size={16}
                />

                <span>
                  Minha conta
                </span>
              </button>

              <button
                type="button"
                role="menuitem"
                onClick={
                  handleChangePassword
                }
                style={{
                  width:
                    "100%",
                  display:
                    "flex",
                  alignItems:
                    "center",
                  gap:
                    "10px",
                  padding:
                    "9px 10px",
                  border:
                    0,
                  borderRadius:
                    "7px",
                  background:
                    "transparent",
                  color:
                    "#334155",
                  cursor:
                    "pointer",
                  textAlign:
                    "left",
                  fontSize:
                    "12px",
                }}
              >
                <KeyRound
                  size={16}
                />

                <span>
                  Alterar senha
                </span>
              </button>

              <div
                style={{
                  margin:
                    "4px 0",
                  borderTop:
                    "1px solid #f1f5f9",
                }}
              />

              <button
                type="button"
                role="menuitem"
                onClick={
                  handleLogout
                }
                style={{
                  width:
                    "100%",
                  display:
                    "flex",
                  alignItems:
                    "center",
                  gap:
                    "10px",
                  padding:
                    "9px 10px",
                  border:
                    0,
                  borderRadius:
                    "7px",
                  background:
                    "transparent",
                  color:
                    "#b91c1c",
                  cursor:
                    "pointer",
                  textAlign:
                    "left",
                  fontSize:
                    "12px",
                }}
              >
                <LogOut
                  size={16}
                />

                <span>
                  Sair
                </span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

export default AppHeader;