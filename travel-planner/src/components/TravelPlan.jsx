import "./TravelPlan.css"
function TravelPlan({ plan }) {
  if (!plan) return null;

  return (
    <div className="travel-plan">
      <div className="plan-header">
        <h2>Destynacja: {plan.destination} 🧭</h2>
        <div className="plan-summary">
          <p><strong>Podsumowanie:</strong> {plan.summary}</p>
        </div>
      </div>

      <div className="itinerary">
        {plan.itinerary.map((day) => (
          <div key={day.day} className="day-card">
            <div className="day-header">
              <span className="day-number">Dzień {day.day}</span>
              <h4>{day.theme}</h4>
            </div>
            <ul>
              {day.activities.map((activity, index) => (
                <li key={index}>{activity}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TravelPlan