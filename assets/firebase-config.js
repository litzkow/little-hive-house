/* Little Hive House: Firebase web config. Paste the values from the Firebase console
   (Project settings → Your apps → Web app → "Config"). These values are public by design;
   the database and storage rules protect the data.
   While apiKey is empty (or live is false) the site works exactly as before: checkout says "Checkout opens soon"
   and the account pages say accounts are opening soon. */
window.LHH_FIREBASE = {
  apiKey: "AIzaSyCQpZCI6XlW9Bh2_66GrOA4Ll5t7XoVyRQ",
  authDomain: "little-hive-house.firebaseapp.com",
  projectId: "little-hive-house",
  storageBucket: "little-hive-house.firebasestorage.app",
  messagingSenderId: "752604920358",
  appId: "1:752604920358:web:39215f4d500467ab72c4e7",
  // false = the store stays "opening soon" for customers until the backend (Stripe, emails) is deployed.
  // The admin page still connects, so the owners can sign in and activate admin access first.
  live: false
};
