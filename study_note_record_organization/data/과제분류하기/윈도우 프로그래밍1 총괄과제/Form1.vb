''' <summary>
''' 총괄과제 폼. 아래 입력 상자의 글자를 위 출력 레이블에 그대로 보여 준다.
''' </summary>
Public Class frmMain
    ''' <summary>
    ''' 입력 상자가 바뀔 때마다 출력 레이블을 비운 뒤 같은 문자열로 다시 쓴다.
    ''' </summary>
    Private Sub txtInput_TextChanged(sender As Object, e As EventArgs) Handles txtInput.TextChanged
        lblOutput.Text = ""
        lblOutput.Text += txtInput.Text
    End Sub
    ''' <summary>
    ''' 폼이 열릴 때 출력 레이블에 포커스를 둔다.
    ''' </summary>
    Private Sub frmMain_Load(sender As Object, e As EventArgs) Handles Me.Load
        lblOutput.Focus()
    End Sub
End Class
