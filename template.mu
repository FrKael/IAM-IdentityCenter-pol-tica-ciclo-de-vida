<h1>AMIs con antigüedad mayor a 3 meses</h1>

<table style="border:1px solid black;">
  <tr>
    <th style="border:1px solid black;">AMI_id</th>
    <th style="border:1px solid black;">Nombre de la AMI</th>
    <th style="border:1px solid black;">Fecha de creación</th>
  </tr>
  {{#.}}
  <tr>
    <td style="border:1px solid black;">{{id}}</td>
    <td style="border:1px solid black;">{{name}}</td>
    <td style="border:1px solid black;">{{date}}</td>
  </tr>
  {{/.}}
</table>