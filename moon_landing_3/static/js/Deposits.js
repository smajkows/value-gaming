import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Title from './Title';
import Table from "@material-ui/core/Table";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import TableCell from "@material-ui/core/TableCell";
import TableBody from "@material-ui/core/TableBody";
import CurrencyFormat from "react-currency-format";
import Button from "@material-ui/core/Button";

function preventDefault(event) {
  event.preventDefault();
}

const useStyles = makeStyles({
  depositContext: {
    flex: 1,
  },
});

class Deposits extends React.Component {

  render() {
    var transactions = this.props.transactions;
    var title = this.props.title;
    var account_name = this.props.account_name;
    return (
        <React.Fragment>
          <Title>{title}</Title>
          <Table size="medium" stickyHeader aria-label="simple table">
            <TableHead>
              <TableRow>
                <TableCell>Ticker</TableCell>
                { account_name ? <TableCell>Account Name</TableCell>:null}
                <TableCell>Trade</TableCell>
                <TableCell>Trade Date</TableCell>
                <TableCell>@</TableCell>
                <TableCell># Shares</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {transactions.map((row, index) => (
                  <TableRow key={index}>
                    <TableCell>{row.symbol}</TableCell>
                    { account_name ? <TableCell>{row.account_name}</TableCell>:null}
                    <TableCell>{row.instruction}</TableCell>
                    <TableCell>{row.transaction_date}</TableCell>
                    <TableCell>
                        <CurrencyFormat value={row.price}
                            displayType={'text'}
                            thousandSeparator={true}
                            decimalScale={2}
                            prefix={'$'} />
                    </TableCell>
                    <TableCell align="right">{row.amount}</TableCell>
                  </TableRow>
              ))}
            </TableBody>
          </Table>
        </React.Fragment>
    );
  }
}

export default Deposits;