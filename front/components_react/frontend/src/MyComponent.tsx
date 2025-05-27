import { Streamlit, withStreamlitConnection } from "streamlit-component-lib";

const MyComponent = () => {
  const handleClick = () => {
    Streamlit.setComponentValue("🔔 Você clicou no botão!");
  };

  return (
    <div style={{ textAlign: "center" }}>
      <h2>🚀 Componente React no Streamlit</h2>
      <button
        style={{
          padding: "10px 20px",
          backgroundColor: "#08bebe",
          border: "none",
          borderRadius: "8px",
          color: "#fff",
          cursor: "pointer"
        }}
        onClick={handleClick}
      >
        Clique aqui
      </button>
    </div>
  );
};

export default withStreamlitConnection(MyComponent);