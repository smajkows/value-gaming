import React from 'react';
// Show Hide Password
import {BrowserRouter as Router, Route} from "react-router-dom";
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import 'bootstrap/dist/css/bootstrap.min.css';
import OverUnder from "./OverUnder";

class Base extends React.Component {
  render() {
    return (
        <React.Fragment>
            <Navbar bg="light" expand="lg">
              <Navbar.Brand href="#home">Value Gaming</Navbar.Brand>
              <Navbar.Toggle aria-controls="basic-navbar-nav" />
              <Navbar.Collapse id="basic-navbar-nav">
                <Nav className="mr-auto">
                    <Nav.Link href="/overunder"> Over/Under </Nav.Link>
                </Nav>
                <Form inline>
                  <Button variant="success">Login</Button>
                </Form>
              </Navbar.Collapse>
            </Navbar>
            <Router>
                <Route path="/overunder" component={OverUnder} />
            </Router>
        </React.Fragment>

    );
  }
}
export default Base;