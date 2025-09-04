import { useNavigate } from "react-router";

const Header = () => {
  const navigate = useNavigate();

  return (
    <header className="flex items-center font-montsera mb-8">
      <p className="mr-4 font-bold">Kakak Agent</p>
      <button className="mr-4" onClick={() => navigate("/")}>
        Home
      </button>
      <button onClick={() => navigate("/ticket")}>Ticket</button>
    </header>
  );
};

export default Header;
