const express = require('express')
const mongoose = require('mongoose')
const cors = require('cors')

const app = express()
const PORT = process.env.PORT || 3001

// Middleware
app.use(cors())
app.use(express.json())

// Rutas
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', service: 'portal-noticias' })
})

app.get('/api/news', (req, res) => {
  res.json({ news: [] })
})

// Iniciar servidor
app.listen(PORT, () => {
  console.log(`🚀 Servidor ejecutándose en puerto ${PORT}`)
})
