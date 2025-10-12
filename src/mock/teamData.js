export const teamData = {
  name: "Philadelphia Eagles",
  manager: "Andres U.",
  image: null, // no image -> use default
  state: "Active",
  league: "NFL Fantasy League 2025",
  players: [
    {
      id: 1,
      name: "Patrick Mahomes",
      position: "QB",
      team: "KC",
      image:
        "https://upload.wikimedia.org/wikipedia/commons/4/4d/Patrick_Mahomes_2023_%28cropped%29.jpg",
      injury: null,
      acquisition: "draft",
    },
    {
      id: 2,
      name: "Travis Kelce",
      position: "TE",
      team: "KC",
      image:
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Travis_Kelce_%2853790185007%29_%28cropped%29.jpg/960px-Travis_Kelce_%2853790185007%29_%28cropped%29.jpg",
      injury: "Questionable",
      acquisition: "trade",
    },
    // ...
  ],
};
