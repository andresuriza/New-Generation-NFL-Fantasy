export default function PlayerFilter({ filter, onChange }) {
  return (
    <div className="player-filter">
      <select
        value={filter.position}
        onChange={(e) => onChange({ ...filter, position: e.target.value })}
      >
        <option value="ALL">Todas las posiciones</option>
        <option value="QB">QB</option>
        <option value="RB">RB</option>
        <option value="FB">FB</option>
        <option value="WR">WR</option>
        <option value="TE">TE</option>
        <option value="OL">OL</option>
        <option value="DL">DL</option>
        <option value="DB">DB</option>
        <option value="LB">LB</option>
      </select>

      <input
        type="text"
        placeholder="Buscar jugador..."
        value={filter.search}
        onChange={(e) => onChange({ ...filter, search: e.target.value })}
      />
    </div>
  );
}
