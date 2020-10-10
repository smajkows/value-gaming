import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Title from './Title';
import CurrencyFormat from "react-currency-format";

function preventDefault(event) {
  event.preventDefault();
}

const useStyles = makeStyles((theme) => ({
  seeMore: {
    marginTop: theme.spacing(3),
  },
}));

class Orders extends React.Component {

  render() {

    const teaser = this.props.teaser;
    const holdings = this.props.my_hold;

    return (
        <React.Fragment>
          <Table size="medium" stickyHeader aria-label="simple table">
            <TableHead>
              <TableRow>
                <TableCell>Ticker</TableCell>
                <TableCell>Avg. Price</TableCell>
                <TableCell># Shares</TableCell>
                <TableCell align={"right"}>Market Value</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {holdings.map((row, index) => (
                  <TableRow key={index}>
                    <TableCell>{row.instrument.symbol}</TableCell>
                    <TableCell>
                      <CurrencyFormat value={row.averagePrice}
                                        displayType={'text'}
                                        thousandSeparator={true}
                                        decimalScale={2}
                                        prefix={'$'} />

                    </TableCell>
                    <TableCell>
                      <CurrencyFormat value={row.longQuantity}
                            displayType={'text'}
                            thousandSeparator={true}
                            decimalScale={2}/>
                    </TableCell>
                    <TableCell align={"right"}>
                      <CurrencyFormat value={row.marketValue}
                            displayType={'text'}
                            thousandSeparator={true}
                            decimalScale={2}
                            prefix={'$'} />
                    </TableCell>
                  </TableRow>
              ))}
              { teaser ? <TableRow><TableCell>Follow this account to see see its full portfolio!</TableCell></TableRow>: <TableRow></TableRow>}
            </TableBody>
          </Table>
        </React.Fragment>
    );
  }
}

export default Orders;