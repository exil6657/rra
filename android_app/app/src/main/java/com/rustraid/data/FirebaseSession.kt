package com.rustraid.data
import com.google.firebase.auth.FirebaseAuth
/** Establishes the authenticated Firebase session required by the database rules. */
object FirebaseSession {
 fun ensureAuthenticated(onReady:()->Unit,onFailure:(Exception)->Unit={}) {
  val auth=FirebaseAuth.getInstance()
  if(auth.currentUser!=null){onReady();return}
  auth.signInAnonymously().addOnSuccessListener{onReady()}.addOnFailureListener{onFailure(it)}
 }
}
