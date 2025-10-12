export default function PlayerFilter({ filter, onChange }) {
  return (
    <div className="player-filter">
      <select
        value={filter.position}
        onChange={(e) => onChange({ ...filter, position: e.target.value })}
      >
        <option value="ALL">All Positions</option>
        <option value="QB">QB</option>
        <option value="RB">RB</option>
        <option value="WR">WR</option>
        <option value="TE">TE</option>
        <option value="K">K</option>
        <option value="DEF">DEF</option>
      </select>

      <input
        type="text"
        placeholder="Search player..."
        value={filter.search}
        onChange={(e) => onChange({ ...filter, search: e.target.value })}
      />
    </div>
  );
}
