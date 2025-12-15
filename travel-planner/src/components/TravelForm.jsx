import "./TravelForm.css"
function TravelForm({ onSubmit }) {

  const handleSubmit = (e) => {
    e.preventDefault();

    const form = e.target;
    const data = new FormData(form);

    const payload = {
      destination: data.get("destination"),
      budget: data.get("budget"),
      recreation_type: data.get("recreation_type"),
      interests: data
        .get("interests")
        .split(",")
        .map(i => i.trim())
        .filter(Boolean),
      date_range: data.get("date_range"),
      travelers_count: Number(data.get("travelers_count")),
      diet: data.get("diet"),
      additional_info: data.get("additional_info")
    };
    console.log(payload);
    onSubmit(payload);
  };

  return (
    <form className="travel-form" onSubmit={handleSubmit}>
      <input name="destination" placeholder="Gdzie jedziesz?" required />

      <select name="budget">
        <option value="Niski">Niski</option>
        <option value="Średni">Średni</option>
        <option value="Wysoki">Wysoki</option>
      </select>

      <select name="recreation_type">
            <option value="Kultura i Technologie">Kultura i Technologie</option>
            <option value="Wypoczynek">Wypoczynek</option>
            <option value="Zwiedzanie">Zwiedzanie</option>
            <option value="Sztuka">Sztuka</option>
            <option value="Popularne miejsca">Popularne miejsca</option>
      </select>

      <input
        name="interests"
        placeholder="Sushi, Retro Gaming"
      />

      <input
        name="date_range"
        placeholder="10-12 październik"
      />

      <input
        name="travelers_count"
        type="number"
        min="1"
        defaultValue="1"
      />

      <input
        name="diet"
        placeholder="Brak alergii"
      />

      <input
        name="additional_info"
        placeholder="Dodatkowe info"
      />

      <button type="submit">Generuj plan</button>
    </form>
  );
}
export default TravelForm
