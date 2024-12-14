import "./Leaderboard.css";

function Leaderboard() {
    
    return (
        <div id="container" className="">
            <h1 className="text-white">Leaderboard</h1>
            <table id="leaderboard">
                <tr>
                    <th>Username</th>
                    <th>Streak</th>
                    <th>Score</th>
                </tr>
                <tr>
                    <td>71_lols</td>
                    <td>108</td>
                    <td>3561</td>
                </tr>
                <tr>
                    <td>beasonhuang</td>
                    <td>3</td>
                    <td>961</td>
                </tr>
                <tr>
                    <td>ypawania</td>
                    <td>18</td>
                    <td>301</td>
                </tr>
                <tr>
                    <td>garyson</td>
                    <td>68</td>
                    <td>181</td>
                </tr>
            </table>
            <a id="home" href="/">Home</a>
        </div>
    )
}

export default Leaderboard;