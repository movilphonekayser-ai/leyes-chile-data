import axios from "axios";
import cheerio from "cheerio";
import dayjs from "dayjs";

export async function scrapeLaws() {
  const url = "https://www.senado.cl/appsenado/index.php?mo=tramitacion&ac=getInformacion";  

  try {
    const { data: html } = await axios.get(url);
    const $ = cheerio.load(html);

    const leyes = [];

    // Seleccionamos las filas de la tabla pública de leyes
    $("table tbody tr").slice(0, 5).each((i, el) => {
      const cols = $(el).find("td");

      const nombre = $(cols[0]).text().trim();
      const fecha = $(cols[1]).text().trim();
      const link = $(cols[0]).find("a").attr("href") || "";

      leyes.push({
        id: i + 1,
        nombre,
        fecha: fecha || dayjs().format("YYYY-MM-DD"),
        url: link.startsWith("http") ? link : `https://www.senado.cl${link}`,
        origen: "Scraping automático"
      });
    });

    return leyes;

  } catch (error) {
    console.error("Error en scraping:", error);
    return [];
  }
}
