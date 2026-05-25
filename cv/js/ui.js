$(document).ready(function () {

    $('.article').each(function () {

        const startDate = $(this).find('.startDate').text().trim();

        if (startDate !== '') {

            const startDateArr = startDate.split('.').map(str => str.trim()).filter(Boolean);
            let endDate = $(this).find('.endDate').text().trim();
            let endDateArr;

            if (endDate === 'today') {

                const now = new Date();
                const year = now.getFullYear();
                const month = String(now.getMonth() + 1).padStart(2, '0');
                const day = String(now.getDate()).padStart(2, '0');

                endDateArr = [year, month, day];
                $(this).find('.endDate').text(`${year}. ${month}. ${day}.`);

            } else {

                endDateArr = endDate.split('.').map(str => str.trim()).filter(Boolean);

                const year = endDateArr[0];
                const month = String(parseInt(endDateArr[1], 10)).padStart(2, '0');
                const day = String(parseInt(endDateArr[2], 10)).padStart(2, '0');

                endDateArr = [year, month, day];
                $(this).find('.endDate').text(`${year}. ${month}. ${day}.`);

            }

            const startDateCalc = new Date(startDateArr[0], startDateArr[1], startDateArr[2]);
            const endDateCalc = new Date(endDateArr[0], endDateArr[1], endDateArr[2]);
            const dateCalc = endDateCalc.getTime() - startDateCalc.getTime();
            const dateCalcResult = dateCalc / (1000 * 60 * 60 * 24);

            let dateResultText;
            const dateResultYear = Math.floor(dateCalcResult / 365);
            const dateResultMonth = Math.round((dateCalcResult - (dateResultYear * 365)) / 30);

            if (dateResultYear === 0 && dateResultMonth === 0) {
                dateResultText = '-';
            } else if (dateResultYear === 0) {
                dateResultText = `${dateResultMonth}개월`;
            } else if (dateResultMonth === 0) {
                dateResultText = `${dateResultYear}년`;
            } else {
                dateResultText = `${dateResultYear}년 ${dateResultMonth}개월`;
            }

            $(this).find('.periodResult').text(`(${dateResultText})`);
        }

    });

});
