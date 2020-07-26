import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Container from "@material-ui/core/Container";
import SignInScreen from "./SignIn";


const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
    backgroundColor: "white",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "300px",
  },
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
}));

export default function Landing() {

    const classes = useStyles();
    return (
        <React.Fragment>
        <Container className={classes.root}>
            <SignInScreen/>
        </Container>
        </React.Fragment>
        )
}

