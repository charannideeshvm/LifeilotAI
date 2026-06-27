// =============================================
// LIFEPILOT AI - FIREBASE CONFIGURATION
// Replace these values with YOUR Firebase config
// from Firebase Console > Project Settings
// =============================================

const firebaseConfig = {
  apiKey: "AIzaSyCoqjmjP5__Azg0Vj29czIfhZq6znAz0hg",
  authDomain: "lifepilot-ai-e8699.firebaseapp.com",
  projectId: "lifepilot-ai-e8699",
  storageBucket: "lifepilot-ai-e8699.firebasestorage.app",
  messagingSenderId: "994657417516",
  appId: "1:994657417516:web:517b95b3427ee11ab39489"
};


// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Make auth and db available globally
const auth = firebase.auth();
const db   = firebase.firestore();