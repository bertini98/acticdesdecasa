const N = { basico: 1, medio: 2, avanzado: 3 } as const;

export default function Bars({ nivel }: { nivel: keyof typeof N }) {
  return (
    <span className={`bars nivel-${nivel}`} aria-hidden>
      {[1, 2, 3].map((i) => (
        <i key={i} className={i <= N[nivel] ? "on" : ""} />
      ))}
    </span>
  );
}
