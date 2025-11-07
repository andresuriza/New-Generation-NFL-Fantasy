import AppRoutes from "./app/routes";
import "./styles/global.css";

export default function App() {
  // Utilizar para borrar datos locales que aun no esten en DB, TEMPORAL
  // localStorage.clear();
  return <AppRoutes />;
}
