import "./DownloadPdfButton.css"

function DownloadPdfButton({ plan }) {

  const downloadPdf = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/save-pdf", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ plan })
      });

      if (!res.ok) {
        throw new Error("Błąd pobierania PDF");
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "Moj_Plan_Podrozy.pdf";
      document.body.appendChild(a);
      a.click();

      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert("Nie udało się pobrać PDF");
    }
  };

  return (
    <button onClick={downloadPdf}>
      📄 Pobierz plan jako PDF
    </button>
  );
}

export default DownloadPdfButton;
