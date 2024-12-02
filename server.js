const express = require("express");
const axios = require("axios");
const multer = require("multer");
const FormData = require("form-data");
const fs = require("fs");

const app = express();
const upload = multer({ dest: "uploads/" });
const FLASK_URL = "http://localhost:5000";

app.use(express.json());

//Esse endPoint é para testar a conexão
app.post("/", upload.single("file"), async (req, res) => {
  try {
    const response = await axios.get(`${FLASK_URL}/`);
    res.json(response.data);
  } catch (error) {
    console.error("Erro:", error.message);
    res
      .status(500)
      .json({ error: "Erro ao iniciar conexão", details: error.message });
  }
});

//Esse endPoint é para o cálculo de HASHES
app.post("/hashAPI", upload.single("file"), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: "Nenhum arquivo enviado" });
    }

    const formData = new FormData();
    formData.append("file", fs.createReadStream(req.file.path));
    formData.append("nomeOriginal", req.file.originalname);

    const response = await axios.post(`${FLASK_URL}/calcula-hash`, formData, {
      headers: {
        ...formData.getHeaders(),
      },
    });

    fs.unlinkSync(req.file.path);

    res.json(response.data);
  } catch (error) {
    console.error("Erro:", error.message);
    res
      .status(500)
      .json({ error: "Erro ao calcular hash", details: error.message });
  }
});

//Esse endPoint é para o cálculo de pixels
app.post("/pixelAPI", upload.single("file"), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: "Nenhum arquivo enviado" });
    }

    const formData = new FormData();
    console.log("Teste JS");
    formData.append("file", fs.createReadStream(req.file.path));
    formData.append("nomeOriginal", req.file.originalname);

    const response = await axios.post(`${FLASK_URL}/calcula-pixels`, formData, {
      headers: {
        ...formData.getHeaders(),
      },
    });

    fs.unlinkSync(req.file.path);
    res.json(response.data);
  } catch (error) {
    console.error("Erro:", error.message);
    res
      .status(500)
      .json({ error: "Erro ao calcular pixels", details: error.message });
  }
});

// Esse endPoint é para redimensionar imagem
app.post("/redimensionaAPI", upload.single("file"), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: "Nenhum arquivo enviado" });
    }

    const { largura, altura } = req.body;
    if (!largura || !altura) {
      return res
        .status(400)
        .json({ error: "Largura e altura são obrigatórios" });
    }

    const formData = new FormData();
    formData.append("file", fs.createReadStream(req.file.path));
    formData.append("largura", largura);
    formData.append("altura", altura);

    const response = await axios.post(
      `${FLASK_URL}/redimensiona-imagem`,
      formData,
      {
        headers: {
          ...formData.getHeaders(),
        },
        responseType: "arraybuffer",
      }
    );

    fs.unlinkSync(req.file.path);

    res.set("Content-Type", "image/png");
    res.send(response.data);
  } catch (error) {
    console.error("Erro:", error);
    res.status(500).json({ error: "Erro ao redimensionar imagem" });
  }
});

// Esse endPoint é para determinar a autenticidade de dois arquivos
app.post(
  "/comparaAPI",
  upload.fields([
    { name: "file1", maxCount: 1 },
    { name: "file2", maxCount: 1 },
  ]),
  async (req, res) => {
    try {
      if (!req.files || !req.files.file1 || !req.files.file2) {
        return res.status(400).json({ error: "Dois arquivos são necessários" });
      }

      const formData = new FormData();
      formData.append("file1", fs.createReadStream(req.files.file1[0].path));
      formData.append("nomeOriginal1", req.files.file1[0].originalname);
      formData.append("file2", fs.createReadStream(req.files.file2[0].path));
      formData.append("nomeOriginal2", req.files.file2[0].originalname);

      const response = await axios.post(
        `${FLASK_URL}/compara-hashes`,
        formData,
        {
          headers: {
            ...formData.getHeaders(),
          },
        }
      );

      fs.unlinkSync(req.files.file1[0].path);
      fs.unlinkSync(req.files.file2[0].path);

      res.json(response.data);
    } catch (error) {
      console.error("Erro:", error);
      res.status(500).json({ error: "Erro ao comparar hashes" });
    }
  }
);

//Esse endPoint é para o aplicar filtro cinza na imagem
app.post("/filtroAPI", upload.single("file"), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: "Nenhum arquivo enviado" });
    }

    const formData = new FormData();
    formData.append("file", fs.createReadStream(req.file.path));

    const response = await axios.post(`${FLASK_URL}/filtro-imagem`, formData, {
      headers: {
        ...formData.getHeaders(),
      },
      responseType: "arraybuffer",
    });

    fs.unlinkSync(req.file.path);

    res.set("Content-Type", "image/png");
    res.send(response.data);
  } catch (error) {
    console.error("Erro:", error);
    res.status(500).json({ error: "Erro ao processar imagem" });
  }
});

app.listen(3000, () => {
  console.log("NodeJS http://127.0.0.1:3000");
});
