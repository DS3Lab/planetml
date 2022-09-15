import discord
from discord.ui import Modal, InputText

class TOMAModel_Feedback(Modal):

    def __init__(self) -> None:

        super().__init__(title="TOMA: Provide Feedback")

        self.add_item(
            InputText(label="Better Response", placeholder = "Response",
            style=discord.InputTextStyle.long)
        )

    async def callback(self, interaction: discord.Interaction):
        
        description = self.children[0].value

        print (description, interaction.message)

        await interaction.response.defer()

class FeedbackView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None) # timeout of the view must be set to None

    @discord.ui.button(label="Submit a Better Reponse!", custom_id="button-submit", style=discord.ButtonStyle.primary, emoji="🚀")
    async def button_callback_feedback(self, button, interaction):
        modal = TOMAModel_Feedback()
        await interaction.response.send_modal(modal)

