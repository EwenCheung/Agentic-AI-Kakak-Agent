import { useNavigate, useLocation } from "react-router-dom";

const Header = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const getLinkClass = (path, hasMargin) => {
    let className = hasMargin ? 'mr-4' : '';
    if (location.pathname === path) {
      className += ' underline';
    }
    return className;
  };

  return (
    <header className="flex items-center font-montsera mb-6">
      <p className="mr-4 text-2xl cursor-pointer" onClick={() => navigate("/")}>Kakak Agent</p>
      <button className={getLinkClass("/", true)} onClick={() => navigate("/")}>
        Home
      </button>
  <button className={getLinkClass("/config", true)} onClick={() => navigate("/config")}>Configuration</button>
  <button className={getLinkClass("/knowledge-base-upload", false)} onClick={() => navigate("/knowledge-base-upload")}>Knowledge Base Upload</button>
    </header>
  );
};

export default Header;
