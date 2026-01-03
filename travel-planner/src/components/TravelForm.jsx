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

      <div>
        <label htmlFor="destination">Miejsce wyjazdu</label>
        <input
          id="destination"
          name="destination"
          placeholder="Gdzie jedziesz?"
          required
        />
      </div>
      
      <div>
        <label htmlFor="budget">Budżet</label>
        <select id="budget" name="budget">
          <option value="Niski">Niski</option>
          <option value="Średni">Średni</option>
          <option value="Wysoki">Wysoki</option>
        </select>
      </div>
      
      <div>
        <label htmlFor="recreation_type">Rodzaj wyjazdu</label>
        <select id="recreation_type" name="recreation_type">
          <option value="Kultura i Technologie">Kultura i Technologie</option>
          <option value="Wypoczynek">Wypoczynek</option>
          <option value="Zwiedzanie">Zwiedzanie</option>
          <option value="Sztuka">Sztuka</option>
          <option value="Popularne miejsca">Popularne miejsca</option>
        </select>
      </div>
      
      <div>
        <label htmlFor="interests">Zainteresowania</label>
        <input
          id="interests"
          name="interests"
          placeholder="Sushi, Retro Gaming"
        />
      </div>
      
      <div>
        <label htmlFor="date_range">Data wyjazdu</label>
        <input
          id="date_range"
          name="date_range"
          placeholder="10-12 październik"
        />
      </div>
      
      <div>
        <label htmlFor="travelers_count">Liczba osób</label>
        <input
          id="travelers_count"
          name="travelers_count"
          type="number"
          min="1"
          defaultValue="1"
        />
      </div>
      
      <div>
        <label htmlFor="diet">Dieta</label>
        <input
          id="diet"
          name="diet"
          placeholder="Brak alergii"
        />
      </div>
      
      <div>
        <label htmlFor="additional_info">Dodatkowe informacje</label>
        <input
          id="additional_info"
          name="additional_info"
          placeholder="Dodatkowe info"
        />
      </div>

  <button type="submit">Generuj plan</button>

</form>
  );
}
export default TravelForm
