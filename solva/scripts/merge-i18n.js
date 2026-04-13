const fs = require('fs')
const path = require('path')

const LOCALES_DIR = path.join(__dirname, '..', 'lib', 'locales')

// New keys to add — organized by section
// Spanish values are the source of truth
const NEW_KEYS = {
  resetPassword: {
    title: {
      es: 'Nueva contraseña',
      en: 'New password',
      fr: 'Nouveau mot de passe',
      pt: 'Nova palavra-passe',
      nl: 'Nieuw wachtwoord',
      de: 'Neues Passwort',
      it: 'Nuova password',
    },
    subtitle: {
      es: 'Elige una contraseña segura para tu cuenta',
      en: 'Choose a secure password for your account',
      fr: 'Choisissez un mot de passe sécurisé pour votre compte',
      pt: 'Escolha uma palavra-passe segura para a sua conta',
      nl: 'Kies een veilig wachtwoord voor je account',
      de: 'Wähle ein sicheres Passwort für dein Konto',
      it: 'Scegli una password sicura per il tuo account',
    },
    verifying: {
      es: 'Verificando...',
      en: 'Verifying...',
      fr: 'Vérification...',
      pt: 'A verificar...',
      nl: 'Verifiëren...',
      de: 'Überprüfen...',
      it: 'Verifica in corso...',
    },
    expired: {
      es: 'El enlace ha expirado. Solicita uno nuevo.',
      en: 'The link has expired. Request a new one.',
      fr: 'Le lien a expiré. Demandez-en un nouveau.',
      pt: 'O link expirou. Solicite um novo.',
      nl: 'De link is verlopen. Vraag een nieuwe aan.',
      de: 'Der Link ist abgelaufen. Fordere einen neuen an.',
      it: 'Il link è scaduto. Richiedine uno nuovo.',
    },
    noMatch: {
      es: 'Las contraseñas no coinciden.',
      en: 'Passwords do not match.',
      fr: 'Les mots de passe ne correspondent pas.',
      pt: 'As palavras-passe não coincidem.',
      nl: 'Wachtwoorden komen niet overeen.',
      de: 'Passwörter stimmen nicht überein.',
      it: 'Le password non coincidono.',
    },
    tooShort: {
      es: 'Mínimo 8 caracteres.',
      en: 'Minimum 8 characters.',
      fr: 'Minimum 8 caractères.',
      pt: 'Mínimo 8 caracteres.',
      nl: 'Minimaal 8 tekens.',
      de: 'Mindestens 8 Zeichen.',
      it: 'Minimo 8 caratteri.',
    },
    success: {
      es: 'Contraseña actualizada. Redirigiendo al login...',
      en: 'Password updated. Redirecting to login...',
      fr: 'Mot de passe mis à jour. Redirection vers la connexion...',
      pt: 'Palavra-passe atualizada. A redirecionar para o login...',
      nl: 'Wachtwoord bijgewerkt. Doorverwijzen naar login...',
      de: 'Passwort aktualisiert. Weiterleitung zum Login...',
      it: 'Password aggiornata. Reindirizzamento al login...',
    },
    submit: {
      es: 'Actualizar contraseña',
      en: 'Update password',
      fr: 'Mettre à jour le mot de passe',
      pt: 'Atualizar palavra-passe',
      nl: 'Wachtwoord bijwerken',
      de: 'Passwort aktualisieren',
      it: 'Aggiorna password',
    },
    backToLogin: {
      es: 'Volver al login →',
      en: 'Back to login →',
      fr: 'Retour à la connexion →',
      pt: 'Voltar ao login →',
      nl: 'Terug naar login →',
      de: 'Zurück zum Login →',
      it: 'Torna al login →',
    },
  },
  categories: {
    cleaning: {
      es: 'Limpieza', en: 'Cleaning', fr: 'Ménage', pt: 'Limpeza', nl: 'Schoonmaak', de: 'Reinigung', it: 'Pulizie',
    },
    plumbing: {
      es: 'Fontanería', en: 'Plumbing', fr: 'Plomberie', pt: 'Canalização', nl: 'Loodgieterij', de: 'Klempnerei', it: 'Idraulica',
    },
    electrical: {
      es: 'Electricidad', en: 'Electrical', fr: 'Électricité', pt: 'Eletricidade', nl: 'Elektra', de: 'Elektrik', it: 'Elettricità',
    },
    painting: {
      es: 'Pintura', en: 'Painting', fr: 'Peinture', pt: 'Pintura', nl: 'Schilderwerk', de: 'Malerei', it: 'Pittura',
    },
    gardening: {
      es: 'Jardinería', en: 'Gardening', fr: 'Jardinage', pt: 'Jardinagem', nl: 'Tuinieren', de: 'Gartenarbeit', it: 'Giardinaggio',
    },
    moving: {
      es: 'Mudanzas', en: 'Moving', fr: 'Déménagement', pt: 'Mudanças', nl: 'Verhuizing', de: 'Umzug', it: 'Traslochi',
    },
    carpentry: {
      es: 'Carpintería', en: 'Carpentry', fr: 'Menuiserie', pt: 'Carpintaria', nl: 'Timmerwerk', de: 'Schreinerei', it: 'Falegnameria',
    },
    tech: {
      es: 'Tecnología', en: 'Technology', fr: 'Technologie', pt: 'Tecnologia', nl: 'Technologie', de: 'Technologie', it: 'Tecnologia',
    },
    design: {
      es: 'Diseño', en: 'Design', fr: 'Design', pt: 'Design', nl: 'Design', de: 'Design', it: 'Design',
    },
    other: {
      es: 'Otro', en: 'Other', fr: 'Autre', pt: 'Outro', nl: 'Overig', de: 'Sonstiges', it: 'Altro',
    },
  },
  proServices: {
    title: {
      es: 'Mis servicios', en: 'My services', fr: 'Mes services', pt: 'Os meus serviços', nl: 'Mijn diensten', de: 'Meine Dienste', it: 'I miei servizi',
    },
    emptyTitle: {
      es: 'Sin servicios aún', en: 'No services yet', fr: 'Aucun service encore', pt: 'Sem serviços ainda', nl: 'Nog geen diensten', de: 'Noch keine Dienste', it: 'Ancora nessun servizio',
    },
    emptySub: {
      es: 'Añade los servicios que ofreces con sus precios', en: 'Add the services you offer with their prices', fr: 'Ajoutez les services que vous proposez avec leurs prix', pt: 'Adicione os serviços que oferece com os seus preços', nl: 'Voeg de diensten toe die je aanbiedt met hun prijzen', de: 'Füge die Dienste hinzu, die du anbietest, mit ihren Preisen', it: 'Aggiungi i servizi che offri con i loro prezzi',
    },
    addFirst: {
      es: '+ Añadir primer servicio', en: '+ Add first service', fr: '+ Ajouter le premier service', pt: '+ Adicionar primeiro serviço', nl: '+ Eerste dienst toevoegen', de: '+ Ersten Dienst hinzufügen', it: '+ Aggiungi primo servizio',
    },
    inactive: {
      es: 'Inactivo', en: 'Inactive', fr: 'Inactif', pt: 'Inativo', nl: 'Inactief', de: 'Inaktiv', it: 'Inattivo',
    },
    deactivate: {
      es: 'Desactivar', en: 'Deactivate', fr: 'Désactiver', pt: 'Desativar', nl: 'Deactiveren', de: 'Deaktivieren', it: 'Disattiva',
    },
    activate: {
      es: 'Activar', en: 'Activate', fr: 'Activer', pt: 'Ativar', nl: 'Activeren', de: 'Aktivieren', it: 'Attiva',
    },
    newService: {
      es: 'Nuevo servicio', en: 'New service', fr: 'Nouveau service', pt: 'Novo serviço', nl: 'Nieuwe dienst', de: 'Neuer Dienst', it: 'Nuovo servizio',
    },
    editService: {
      es: 'Editar servicio', en: 'Edit service', fr: 'Modifier le service', pt: 'Editar serviço', nl: 'Dienst bewerken', de: 'Dienst bearbeiten', it: 'Modifica servizio',
    },
    titleLabel: {
      es: 'Título *', en: 'Title *', fr: 'Titre *', pt: 'Título *', nl: 'Titel *', de: 'Titel *', it: 'Titolo *',
    },
    titlePlaceholder: {
      es: 'Ej: Reparación de fugas', en: 'E.g. Leak repair', fr: 'Ex: Réparation de fuites', pt: 'Ex: Reparação de fugas', nl: 'bijv. Lekreparatie', de: 'z.B. Leck-Reparatur', it: 'Es: Riparazione perdite',
    },
    descLabel: {
      es: 'Descripción', en: 'Description', fr: 'Description', pt: 'Descrição', nl: 'Beschrijving', de: 'Beschreibung', it: 'Descrizione',
    },
    descPlaceholder: {
      es: 'Describe el servicio...', en: 'Describe the service...', fr: 'Décrivez le service...', pt: 'Descreva o serviço...', nl: 'Beschrijf de dienst...', de: 'Beschreibe den Dienst...', it: 'Descrivi il servizio...',
    },
    categoryLabel: {
      es: 'Categoría', en: 'Category', fr: 'Catégorie', pt: 'Categoria', nl: 'Categorie', de: 'Kategorie', it: 'Categoria',
    },
    priceType: {
      es: 'Tipo de precio', en: 'Price type', fr: 'Type de prix', pt: 'Tipo de preço', nl: 'Prijstype', de: 'Preistyp', it: 'Tipo di prezzo',
    },
    priceFixed: {
      es: 'Precio fijo', en: 'Fixed price', fr: 'Prix fixe', pt: 'Preço fixo', nl: 'Vaste prijs', de: 'Festpreis', it: 'Prezzo fisso',
    },
    priceFrom: {
      es: 'Desde', en: 'From', fr: 'À partir de', pt: 'Desde', nl: 'Vanaf', de: 'Ab', it: 'Da',
    },
    priceHourly: {
      es: 'Por hora', en: 'Per hour', fr: "À l'heure", pt: 'Por hora', nl: 'Per uur', de: 'Pro Stunde', it: "All'ora",
    },
    priceQuote: {
      es: 'Presupuesto', en: 'Quote', fr: 'Devis', pt: 'Orçamento', nl: 'Offerte', de: 'Angebot', it: 'Preventivo',
    },
    priceLabel: {
      es: 'Precio', en: 'Price', fr: 'Prix', pt: 'Preço', nl: 'Prijs', de: 'Preis', it: 'Prezzo',
    },
    durationLabel: {
      es: 'Duración estimada (horas)', en: 'Estimated duration (hours)', fr: 'Durée estimée (heures)', pt: 'Duração estimada (horas)', nl: 'Geschatte duur (uren)', de: 'Geschätzte Dauer (Stunden)', it: 'Durata stimata (ore)',
    },
    addService: {
      es: 'Añadir servicio', en: 'Add service', fr: 'Ajouter le service', pt: 'Adicionar serviço', nl: 'Dienst toevoegen', de: 'Dienst hinzufügen', it: 'Aggiungi servizio',
    },
    titleRequired: {
      es: 'El título es obligatorio', en: 'Title is required', fr: 'Le titre est obligatoire', pt: 'O título é obrigatório', nl: 'Titel is verplicht', de: 'Titel ist erforderlich', it: 'Il titolo è obbligatorio',
    },
    deleteConfirm: {
      es: '¿Eliminar servicio?', en: 'Delete service?', fr: 'Supprimer le service ?', pt: 'Eliminar serviço?', nl: 'Dienst verwijderen?', de: 'Dienst löschen?', it: 'Eliminare servizio?',
    },
  },
  referrals: {
    title: {
      es: 'Programa de referidos', en: 'Referral program', fr: 'Programme de parrainage', pt: 'Programa de referências', nl: 'Verwijzingsprogramma', de: 'Empfehlungsprogramm', it: 'Programma referral',
    },
    heroTitle: {
      es: 'Invita y gana', en: 'Invite and earn', fr: 'Invitez et gagnez', pt: 'Convide e ganhe', nl: 'Nodig uit en verdien', de: 'Einladen und verdienen', it: 'Invita e guadagna',
    },
    heroDesc: {
      es: 'Por cada amigo que completa su primer pago en Solva, ambos recibís una recompensa.', en: 'For every friend who completes their first payment on Solva, you both receive a reward.', fr: 'Pour chaque ami qui effectue son premier paiement sur Solva, vous recevez tous les deux une récompense.', pt: 'Por cada amigo que completa o seu primeiro pagamento no Solva, ambos recebem uma recompensa.', nl: 'Voor elke vriend die zijn eerste betaling op Solva voltooit, ontvangen jullie beiden een beloning.', de: 'Für jeden Freund, der seine erste Zahlung auf Solva abschließt, erhaltet ihr beide eine Belohnung.', it: 'Per ogni amico che completa il primo pagamento su Solva, entrambi ricevete una ricompensa.',
    },
    codeLabel: {
      es: 'Tu código de referido', en: 'Your referral code', fr: 'Ton code de parrainage', pt: 'O seu código de referência', nl: 'Jouw verwijzingscode', de: 'Dein Empfehlungscode', it: 'Il tuo codice referral',
    },
    copied: {
      es: '¡Copiado!', en: 'Copied!', fr: 'Copié !', pt: 'Copiado!', nl: 'Gekopieerd!', de: 'Kopiert!', it: 'Copiato!',
    },
    tapToCopy: {
      es: 'Toca para copiar', en: 'Tap to copy', fr: 'Appuyez pour copier', pt: 'Toque para copiar', nl: 'Tik om te kopiëren', de: 'Tippen zum Kopieren', it: 'Tocca per copiare',
    },
    shareCode: {
      es: 'Compartir mi código', en: 'Share my code', fr: 'Partager mon code', pt: 'Partilhar o meu código', nl: 'Mijn code delen', de: 'Meinen Code teilen', it: 'Condividi il mio codice',
    },
    statInvited: {
      es: 'Invitados', en: 'Invited', fr: 'Invités', pt: 'Convidados', nl: 'Uitgenodigd', de: 'Eingeladen', it: 'Invitati',
    },
    statCompleted: {
      es: 'Completados', en: 'Completed', fr: 'Complétés', pt: 'Concluídos', nl: 'Voltooid', de: 'Abgeschlossen', it: 'Completati',
    },
    statPending: {
      es: 'Pendientes', en: 'Pending', fr: 'En attente', pt: 'Pendentes', nl: 'In afwachting', de: 'Ausstehend', it: 'In attesa',
    },
    statEarned: {
      es: 'Ganado', en: 'Earned', fr: 'Gagné', pt: 'Ganho', nl: 'Verdiend', de: 'Verdient', it: 'Guadagnato',
    },
    howItWorks: {
      es: '¿Cómo funciona?', en: 'How does it work?', fr: 'Comment ça marche ?', pt: 'Como funciona?', nl: 'Hoe werkt het?', de: 'Wie funktioniert es?', it: 'Come funziona?',
    },
    step1: {
      es: 'Comparte tu código con amigos', en: 'Share your code with friends', fr: 'Partagez votre code avec des amis', pt: 'Partilhe o seu código com amigos', nl: 'Deel je code met vrienden', de: 'Teile deinen Code mit Freunden', it: 'Condividi il tuo codice con gli amici',
    },
    step2: {
      es: 'Se registran con tu código', en: 'They register with your code', fr: "Ils s'inscrivent avec votre code", pt: 'Registam-se com o seu código', nl: 'Ze registreren met jouw code', de: 'Sie registrieren sich mit deinem Code', it: 'Si registrano con il tuo codice',
    },
    step3: {
      es: 'Completan su primer pago', en: 'They complete their first payment', fr: 'Ils effectuent leur premier paiement', pt: 'Completam o seu primeiro pagamento', nl: 'Ze voltooien hun eerste betaling', de: 'Sie schließen ihre erste Zahlung ab', it: 'Completano il primo pagamento',
    },
    step4: {
      es: 'Ambos recibís una recompensa', en: 'You both receive a reward', fr: 'Vous recevez tous les deux une récompense', pt: 'Ambos recebem uma recompensa', nl: 'Jullie ontvangen beiden een beloning', de: 'Ihr beide erhaltet eine Belohnung', it: 'Entrambi ricevete una ricompensa',
    },
    yourReferrals: {
      es: 'Tus referidos', en: 'Your referrals', fr: 'Vos parrainages', pt: 'As suas referências', nl: 'Jouw verwijzingen', de: 'Deine Empfehlungen', it: 'I tuoi referral',
    },
    emptyTitle: {
      es: 'Aún no tienes referidos', en: 'No referrals yet', fr: 'Aucun parrainage encore', pt: 'Ainda não tem referências', nl: 'Nog geen verwijzingen', de: 'Noch keine Empfehlungen', it: 'Ancora nessun referral',
    },
    emptySub: {
      es: 'Comparte tu código y empieza a ganar', en: 'Share your code and start earning', fr: 'Partagez votre code et commencez à gagner', pt: 'Partilhe o seu código e comece a ganhar', nl: 'Deel je code en begin met verdienen', de: 'Teile deinen Code und fang an zu verdienen', it: 'Condividi il tuo codice e inizia a guadagnare',
    },
  },
  admin: {
    title: {
      es: 'Panel Admin', en: 'Admin Panel', fr: "Panneau d'administration", pt: 'Painel Admin', nl: 'Beheerderspaneel', de: 'Admin-Panel', it: 'Pannello Admin',
    },
    tabKYC: {
      es: 'KYC', en: 'KYC', fr: 'KYC', pt: 'KYC', nl: 'KYC', de: 'KYC', it: 'KYC',
    },
    tabDisputes: {
      es: 'Disputas', en: 'Disputes', fr: 'Litiges', pt: 'Disputas', nl: 'Geschillen', de: 'Streitfälle', it: 'Dispute',
    },
    tabPayments: {
      es: 'Pagos', en: 'Payments', fr: 'Paiements', pt: 'Pagamentos', nl: 'Betalingen', de: 'Zahlungen', it: 'Pagamenti',
    },
    noVerifications: {
      es: 'No hay verificaciones', en: 'No verifications', fr: 'Aucune vérification', pt: 'Sem verificações', nl: 'Geen verificaties', de: 'Keine Verifizierungen', it: 'Nessuna verifica',
    },
    noDisputes: {
      es: 'No hay disputas', en: 'No disputes', fr: 'Aucun litige', pt: 'Sem disputas', nl: 'Geen geschillen', de: 'Keine Streitfälle', it: 'Nessuna disputa',
    },
    noPayments: {
      es: 'No hay pagos', en: 'No payments', fr: 'Aucun paiement', pt: 'Sem pagamentos', nl: 'Geen betalingen', de: 'Keine Zahlungen', it: 'Nessun pagamento',
    },
    approve: {
      es: 'Aprobar', en: 'Approve', fr: 'Approuver', pt: 'Aprovar', nl: 'Goedkeuren', de: 'Genehmigen', it: 'Approva',
    },
    reject: {
      es: 'Rechazar', en: 'Reject', fr: 'Rejeter', pt: 'Rejeitar', nl: 'Afwijzen', de: 'Ablehnen', it: 'Rifiuta',
    },
    favorClient: {
      es: 'Favor cliente', en: 'Favor client', fr: 'En faveur du client', pt: 'Favor cliente', nl: 'Klant bevoordelen', de: 'Zugunsten Kunde', it: 'Favore cliente',
    },
    favorPro: {
      es: 'Favor pro', en: 'Favor pro', fr: 'En faveur du pro', pt: 'Favor pro', nl: 'Pro bevoordelen', de: 'Zugunsten Pro', it: 'Favore pro',
    },
  },
  availability: {
    available: {
      es: 'Disponible', en: 'Available', fr: 'Disponible', pt: 'Disponível', nl: 'Beschikbaar', de: 'Verfügbar', it: 'Disponibile',
    },
    busy: {
      es: 'Ocupado', en: 'Busy', fr: 'Occupé', pt: 'Ocupado', nl: 'Bezet', de: 'Beschäftigt', it: 'Occupato',
    },
    unavailable: {
      es: 'No disponible', en: 'Unavailable', fr: 'Indisponible', pt: 'Indisponível', nl: 'Niet beschikbaar', de: 'Nicht verfügbar', it: 'Non disponibile',
    },
  },
  status: {
    open: {
      es: 'Abierto', en: 'Open', fr: 'Ouvert', pt: 'Aberto', nl: 'Open', de: 'Offen', it: 'Aperto',
    },
    inProgress: {
      es: 'En progreso', en: 'In progress', fr: 'En cours', pt: 'Em progresso', nl: 'In uitvoering', de: 'In Bearbeitung', it: 'In corso',
    },
    completed: {
      es: 'Completado', en: 'Completed', fr: 'Terminé', pt: 'Concluído', nl: 'Voltooid', de: 'Abgeschlossen', it: 'Completato',
    },
    cancelled: {
      es: 'Cancelado', en: 'Cancelled', fr: 'Annulé', pt: 'Cancelado', nl: 'Geannuleerd', de: 'Abgebrochen', it: 'Annullato',
    },
    pending: {
      es: 'Pendiente', en: 'Pending', fr: 'En attente', pt: 'Pendente', nl: 'In afwachting', de: 'Ausstehend', it: 'In attesa',
    },
    accepted: {
      es: 'Aceptada', en: 'Accepted', fr: 'Acceptée', pt: 'Aceite', nl: 'Geaccepteerd', de: 'Angenommen', it: 'Accettata',
    },
    rejected: {
      es: 'Rechazada', en: 'Rejected', fr: 'Rejetée', pt: 'Rejeitada', nl: 'Afgewezen', de: 'Abgelehnt', it: 'Rifiutata',
    },
    rewarded: {
      es: 'Recompensado', en: 'Rewarded', fr: 'Récompensé', pt: 'Recompensado', nl: 'Beloond', de: 'Belohnt', it: 'Ricompensato',
    },
  },
}

const LANGS = ['es', 'en', 'fr', 'pt', 'nl', 'de', 'it']

function deepMerge(target, source) {
  for (const key of Object.keys(source)) {
    if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
      if (!target[key]) target[key] = {}
      deepMerge(target[key], source[key])
    } else {
      target[key] = source[key]
    }
  }
  return target
}

// Transform NEW_KEYS from { section: { key: { lang: value } } }
// to per-language { section: { key: value } }
function getKeysForLang(lang) {
  const result = {}
  for (const [section, keys] of Object.entries(NEW_KEYS)) {
    result[section] = {}
    for (const [key, translations] of Object.entries(keys)) {
      result[section][key] = translations[lang] || translations['en']
    }
  }
  return result
}

let totalAdded = 0

for (const lang of LANGS) {
  const filePath = path.join(LOCALES_DIR, `${lang}.json`)
  const existing = JSON.parse(fs.readFileSync(filePath, 'utf8'))
  const newKeys = getKeysForLang(lang)

  // Count new keys
  let added = 0
  for (const [section, keys] of Object.entries(newKeys)) {
    for (const key of Object.keys(keys)) {
      if (!existing[section] || !existing[section][key]) added++
    }
  }

  deepMerge(existing, newKeys)
  fs.writeFileSync(filePath, JSON.stringify(existing, null, 2) + '\n')
  console.log(`${lang}.json: merged ${added} new keys`)
  totalAdded += added
}

console.log(`\nTotal: ${totalAdded} keys added across ${LANGS.length} languages`)
