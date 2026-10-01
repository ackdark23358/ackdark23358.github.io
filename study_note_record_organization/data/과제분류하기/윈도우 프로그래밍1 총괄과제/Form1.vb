Public Class frmMain
    Private Sub txtInput_TextChanged(sender As Object, e As EventArgs) Handles txtInput.TextChanged
        lblOutput.Text = ""
        lblOutput.Text += txtInput.Text
    End Sub
    Private Sub frmMain_Load(sender As Object, e As EventArgs) Handles Me.Load
        lblOutput.Focus()
    End Sub
End Class
