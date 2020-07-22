// Configure Firebase.
import firebase from "firebase";
import React from "react";
import StyledFirebaseAuth from "react-firebaseui/StyledFirebaseAuth";
import Button from "@material-ui/core/Button";

var config = {
apiKey: "AIzaSyCVoNcuKeb_1Pyer_7OWgZLzBMJktOmoCs",
authDomain: "project-moon-landing.firebaseapp.com",
databaseURL: "https://project-moon-landing.firebaseio.com",
projectId: "project-moon-landing",
storageBucket: "project-moon-landing.appspot.com",
messagingSenderId: "858100056639",
appId: "1:858100056639:web:803c0797ff99668fb7ee8a",
measurementId: "G-2LRYDWY7D7"
};

firebase.initializeApp(config);

// FirebaseUI config.
var uiConfig = {
signInSuccessUrl: '/',
signInOptions: [
  firebase.auth.GoogleAuthProvider.PROVIDER_ID,
  firebase.auth.EmailAuthProvider.PROVIDER_ID

],
//credentialHelper: firebaseui.auth.CredentialHelper.NONE,
// Terms of service url.
tosUrl: '<your-tos-url>'
};

class SignInScreen extends React.Component {

  // The component's Local state.
  constructor() {
      super();
      this.state = {
    isSignedIn: false // Local signed-in state.
  };
  }


  // Listen to the Firebase Auth state and set the local state.
  componentDidMount() {
    this.unregisterAuthObserver = firebase.auth().onAuthStateChanged((user) => this.setState({isSignedIn: !!user})
    );
    firebase.auth().onAuthStateChanged(function (user) {
        if (user) {
          user.getIdToken().then(function (token) {
            document.cookie = "token=" + token;
          });
        } else {
          document.cookie = "token=";
        }
      });
  }

  // Make sure we un-register Firebase observers when the component unmounts.
  componentWillUnmount() {
    this.unregisterAuthObserver();

    firebase.auth().onAuthStateChanged(function (user) {
        if (user) {
          user.getIdToken().then(function (token) {
            document.cookie = "token=" + token;
          });
        } else {
          document.cookie = "token=";
        }
      });
  }

  render() {
    if (!this.state.isSignedIn) {
      return (
        <div>
          <StyledFirebaseAuth uiConfig={uiConfig} firebaseAuth={firebase.auth()}/>
        </div>
      );
    }
    return (
      <div>
        <p>Welcome {firebase.auth().currentUser.displayName}! You are now signed-in!</p>
        <Button color="secondary" onClick={() => firebase.auth().signOut()}>Sign-out</Button>
      </div>
    );
  }
}

export default SignInScreen;