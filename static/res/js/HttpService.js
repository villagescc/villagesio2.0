class HttpService{

    get(url){
        return new Promise((resolve, reject) => {
            $.ajax({
                url: url,
                method: 'GET',
                success: data => resolve(data),
                error: err => reject(err)
            })
        });
    }

    post(url, data){
        return new Promise((resolve, reject) => {
            $.ajax({
                url: url,
                method: 'POST',
                data: JSON.stringify(data),
                contentType: "application/json; charset=utf-8",
                success: data => resolve(data),
                error: err => reject(err)
            })
        });
    }

}