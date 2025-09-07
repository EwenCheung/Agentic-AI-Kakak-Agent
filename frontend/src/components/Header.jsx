import { useNavigate } from "react-router";

const Header = () => {
  const navigate = useNavigate();

  return (
    <header className="flex items-center font-montsera mb-6">
      <p className="mr-4 font-bold">Kakak Agent</p>
      <button className="mr-4" onClick={() => navigate("/")}>
        Home
      </button>
  <button className="mr-4" onClick={() => navigate("/config")}>Configuration</button>
  <button onClick={() => navigate("/knowledge-base-upload")}>Knowledge Base Upload</button>
    </header>
  );
};

export default Header;
