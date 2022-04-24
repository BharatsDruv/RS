// const button = document.querySelector('.btn')
// const form   = document.querySelector('.form')

// button.addEventListener('click', function() {
//    form.classList.add('form--no') 
// });

const thisForm = document.getElementById('myForm');
thisForm.addEventListener('submit', async function (e) {
    e.preventDefault();
    // const formData = new FormData(thisForm).entries()
    //  console.log(formData);
    // const response = await fetch('http://127.0.0.1:5000/test', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json'},
    //     body: JSON.stringify(Object.fromEntries(formData))
    // });

    let formData = new FormData(thisForm);
    formData.append('a' , 5)
    formData.append('b' , 5)
    formData.append('c' , 5)
    formData.append('d' , 5)
    formData.append('e' , 5)
    formData.append('f' , 5)
    formData.append('g' , 5)
    formData.append('h' , 5)
    formData.append('i' , 5)

    const response = axios.post("http://127.0.0.1:5000/test", {
        values: JSON.stringify(Object.fromEntries(formData))
    }).then(function (response) {
        console.log(response)
        // do whatever you want if console is [object object] then stringify the response
    })


    //  const result = await response.json();
    console.log(response)
});