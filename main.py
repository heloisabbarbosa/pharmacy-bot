import discord
import os
import re
import logging
from collections import defaultdict
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Select, Modal, TextInput
from datetime import datetime, timedelta
import pytz  
import random
import string
from discord.ext import tasks
import asyncio

id_do_servidor = # id do servidor
id_do_canal_principal =   # Canal onde a mensagem fixa aparece
id_do_canal_registros =   # Canal onde os registros serão guardados
id_do_canal_controle = # pra pesquisar por id
id_do_canal_registros2 = 
id_canal_laudos =  
id_canal_laudosrg = 
id_canal_aprovacao = 
id_canal_metas = 

percentuais_personalizados = {}
# Estrutura para armazenar os dados
metas = {}  # Meta de cada usuário {user_id: meta}
farme_parcial = {}  # Total contabilizado {user_id: total_farmado}
pendente = {}  # Pendências aguardando aprovação {message_id: {"user_id": X, "quantidade": Y}}
mensagens_metas = {}  # Armazena {user_id: message_id}
solicitacoes_farme = {}  # Dicionário para armazenar as solicitações pendentes {usuario_id: quantidade}


class BotClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False
        self.channel_message_id_principal = None
        self.channel_message_id_controle = None
        self.channel_message_id_laudos = None
        self.channel_message_id_farmacia = None

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:  
            await tree.sync(guild=discord.Object(id=id_do_servidor))
            self.synced = True
        print(f"Bot conectado como {self.user}.")

        self.add_view(self.create_button_view())
        self.add_view(self.create_control_view())
        self.add_view(self.create_laudos_button_view())
        
        # Configuração do canal principal
        principal_channel = self.get_channel(id_do_canal_principal)
        if principal_channel is None:
            print(f"Erro: Não consegui acessar o canal com ID {id_do_canal_principal}.")
        else:
            try:
                embed_principal = self.create_embed()  
                if self.channel_message_id_principal:
                    message = await principal_channel.fetch_message(self.channel_message_id_principal)
                    await message.edit(embed=embed_principal, view=self.create_button_view())  
                else:
                    sent_message = await principal_channel.send(embed=embed_principal, view=self.create_button_view())
                    self.channel_message_id_principal = sent_message.id
                    print(f"Mensagem fixa enviada no canal principal com ID {sent_message.id}.")
            except Exception as e:
                print(f"Erro ao configurar o canal principal: {e}")


        # Configuração do canal de controle
        controle_channel = self.get_channel(id_do_canal_controle)
        if controle_channel is None:
            print(f"Erro: Não consegui acessar o canal com ID {id_do_canal_controle}.")
        else:
            try:
                embed_controle = discord.Embed(
                    title="📝 Controle da Farmácia - Vendas\u200b",
                    description="Clique no botão abaixo para consultar um cliente e verificar o total de remédios comprados.",
                    color=discord.Colour(value=0xB90E0A)
                )
                #embed_controle.set_image(url="https://i.ibb.co/5Wqst5q/EMSNEXUS.png")
                embed_controle.set_image(url="https://i.ibb.co/xSDqRD1S/discord-profile-pictures-jktaycg4bu6l4s89.jpg")
                embed_controle.set_footer(text=f"• Verificado: HP")
                if self.channel_message_id_controle:
                    message = await controle_channel.fetch_message(self.channel_message_id_controle)
                    await message.edit(embed=embed_controle, view=self.create_control_view())
                else:
                    sent_message = await controle_channel.send(embed=embed_controle, view=self.create_control_view())
                    self.channel_message_id_controle = sent_message.id
                    print(f"Mensagem fixa enviada no canal de controle com ID {sent_message.id}.")
            except Exception as e:
                print(f"Erro ao configurar o canal de controle: {e}")

        

        # Configuração do canal de laudos
        laudos_channel = self.get_channel(id_canal_laudos)
        if laudos_channel is None:
            print(f"Erro: Não consegui acessar o canal com ID {id_canal_laudos}.")
        else:
            try:
                embed_laudos = discord.Embed(
                    title="📋 Laudo de Medicamentos\u200b",
                    description="Clique no botão abaixo para registrar um laudo.",
                    color=discord.Colour(value=0xB90E0A)
                )
                embed_laudos.set_image(url="https://i.ibb.co/xSDqRD1S/discord-profile-pictures-jktaycg4bu6l4s89.jpg")
                embed_laudos.set_footer(text="Laudos gerados automaticamente")
    
                if self.channel_message_id_laudos:
                    message = await laudos_channel.fetch_message(self.channel_message_id_laudos)
                    await message.edit(embed=embed_laudos, view=self.create_laudos_button_view())
                else:
                    sent_message = await laudos_channel.send(embed=embed_laudos, view=self.create_laudos_button_view())
                    self.channel_message_id_laudos = sent_message.id
                    print(f"Mensagem fixa enviada no canal de laudos com ID {sent_message.id}.")
            except Exception as e:
                print(f"Erro ao configurar o canal de laudos: {e}")

    

    def create_embed(self):
        tz_brazil = pytz.timezone("America/Sao_Paulo")
        now = datetime.now(tz_brazil).strftime("%d/%m/%Y %H:%M:%S")

        embed = discord.Embed(
        title="💊 Vendas remédios farmácia\n",
            description="O não cadastramento da venda pode ser considerado caixa 2,"
            " que resulta em banimento direto pela administração da cidade!\n\n"
            "💡 Qualquer dúvida ou problema com o bot/vendas, você pode abrir um ticket pra falar conosco!",
            color=discord.Colour(value=0xB90E0A)  
        )
        embed.set_image(url="https://i.ibb.co/xSDqRD1S/discord-profile-pictures-jktaycg4bu6l4s89.jpg")
        #embed.set_image(url="https://i.ibb.co/5Wqst5q/EMSNEXUS.png")

        now = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y • %H:%M:%S')
        embed.set_footer(text=f"{now}")
        return embed
    


    async def gerar_transcript_txt(channel):
        transcript = []
        timezone = pytz.timezone('America/Sao_Paulo')
        async for message in channel.history(oldest_first=True):
            timestamp = message.created_at.astimezone(timezone).strftime('%d/%m/%Y %H:%M:%S')
            transcript.append(f"[{timestamp}] {message.author.display_name}: {message.content}")

        transcript_content = "\n".join(transcript)
        return transcript_content

    async def salvar_transcript_txt(transcript_content, channel_id, user_id):
        filename = f"transcripts/{channel_id}/{user_id}.txt"
        os.makedirs(os.path.dirname(filename), exist_ok=True)  
        with open(filename, "w", encoding="utf-8") as file:
            file.write(transcript_content)
        return filename
    
    async def notificar_usuario_com_txt(user, responsavel, arquivo_transcript):
        """Notifica o usuário sobre o encerramento do ticket e envia o transcript."""
        if isinstance(responsavel, discord.Member):
            responsavel_mention = responsavel.mention
        else:
            responsavel_mention = "Ninguém"

        embed = discord.Embed(
            title="🎫 Ticket Encerrado",
            description=f"Seu ticket foi encerrado.\n\n**Responsável:** {responsavel_mention}\n",
            color=discord.Colour(value=0xB90E0A),
        )
        embed.set_footer(text="Obrigado por utilizar nosso sistema de suporte!")
        embed.set_thumbnail(url="https://i.ibb.co/xSDqRD1S/discord-profile-pictures-jktaycg4bu6l4s89.jpg")

        try:
            with open(arquivo_transcript, "rb") as file:
                await user.send(embed=embed, file=discord.File(file, "transcript.txt"))
        except discord.Forbidden:
            print(f"Não foi possível enviar mensagem privada para {user}.")




    
    
    class FecharTicketButton(Button):
        def __init__(self, channel, user, responsavel, created_at):
            super().__init__(label="Fechar Ticket", style=discord.ButtonStyle.danger)
            self.channel = channel
            self.user = user
            self.responsavel = responsavel
            self.created_at = created_at

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)

            timezone = pytz.timezone('America/Sao_Paulo')
            created_at_formatted = self.created_at.astimezone(timezone).strftime("%d/%m/%Y %H:%M:%S")

            responsavel = self.responsavel or "Ninguém assumiu o ticket"
            embed = discord.Embed(
                title="🎫 Ticket Encerrado",
                description=(
                    f"Seu ticket foi encerrado.\n"
                    f"Segue o histórico do ticket em anexo.\n\n"
                    f"💊 **Responsável:** {responsavel.mention if isinstance(responsavel, discord.Member) else responsavel}\n"
                    f"📅 **Aberto em:** {created_at_formatted}\n"
                ),
                color=discord.Colour(value=0xB90E0A),
            )
            embed.set_footer(text="Obrigado por utilizar nosso sistema de suporte!")
            embed.set_thumbnail(url="https://i.ibb.co/xSDqRD1S/discord-profile-pictures-jktaycg4bu6l4s89.jpg")

            transcript_content = await BotClient.gerar_transcript_txt(self.channel)
            arquivo_transcript = await BotClient.salvar_transcript_txt(transcript_content, self.channel.id, self.user.id)

            try:
                with open(arquivo_transcript, "rb") as file:
                    await self.user.send(embed=embed, file=discord.File(file, "transcript.txt"))
            except discord.Forbidden:
                print(f"Não foi possível enviar mensagem privada para {self.user}.")

            category = self.channel.category
            await self.channel.delete(reason="Ticket fechado.")
            if category and len(category.channels) == 0:
                await category.delete(reason="Categoria excluída porque ficou vazia.")








    # Botão para assumir o ticket
    class AssumirTicketButton(Button):
        def __init__(self, channel, role_ids):
            super().__init__(label="Assumir Ticket", style=discord.ButtonStyle.primary)
            self.channel = channel
            self.role_ids = role_ids

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)

            has_permission = any(
                discord.utils.get(interaction.guild.roles, id=role_id) in interaction.user.roles
                for role_id in self.role_ids
            )

            if not has_permission:
                await interaction.followup.send("Você não tem permissão para assumir este ticket.", ephemeral=True)
                return

            await self.channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
            for item in self.view.children:
                if isinstance(item, BotClient.FecharTicketButton):
                    item.responsavel = interaction.user

            embed = discord.Embed(
                title="🎉 Ticket Assumido",
                description=f"{interaction.user.mention} assumiu o ticket e irá ajudá-lo a partir de agora!",
                color=discord.Color.green(),
            )
            embed.set_footer(text=f"Responsável: {interaction.user.display_name}")
            embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else None)

            await self.channel.send(embed=embed)

    


    class AbrirTicketButton(Button):
        def __init__(self, custom_id):
            super().__init__(label="Abrir Ticket", style=discord.ButtonStyle.success, custom_id=custom_id)

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)

            guild = interaction.guild
            user = interaction.user

            created_at = datetime.now()

            category_name = "Tickets-Farmácia"
            category = discord.utils.get(guild.categories, name=category_name)
            if not category:
                category = await guild.create_category(name=category_name, reason="Categoria para tickets")

            role_ids_responsaveis = [1310750636836519987, 1310763281232822343]

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),  # Bloquear acesso para todos
                user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),  # Permitir acesso para o usuário
            }

            # Adicionar permissões para os cargos responsáveis
            for role_id in role_ids_responsaveis:
                role = guild.get_role(role_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)

            # Criar canal para o ticket
            ticket_channel = await guild.create_text_channel(
                name=f"ticket-{user.name}",
                overwrites=overwrites,
                category=category,
                reason=f"Ticket criado por {user.name}",
            )

            fechar_view = View(timeout=None)
            fechar_view.add_item(BotClient.AssumirTicketButton(channel=ticket_channel, role_ids=[1310750636836519987, 1310763281232822343]))
            fechar_view.add_item(BotClient.FecharTicketButton(channel=ticket_channel, user=user, responsavel=None, created_at=created_at))

            embed = discord.Embed(
                title="🎫 Ticket Criado",
                description=f"Olá {user.mention}, seu ticket foi criado com sucesso! Um gerente irá ajudá-lo em breve.\n\n"
                            f"Por favor, aguarde um momento e explique sua dúvida ou solicitação aqui.",
                color=discord.Color.blue(),
            )
            embed.set_footer(text="Você será atendido assim que um responsável pegar o ticket!")
            embed.set_thumbnail(url="https://i.ibb.co/xSDqRD1S/discord-profile-pictures-jktaycg4bu6l4s89.jpg")

            await ticket_channel.send(
                content=f"<@&1310750636836519987>",
                embed=embed,
                view=fechar_view,
            )

            await interaction.followup.send(
                f"Seu ticket foi criado com sucesso! Confira o canal: {ticket_channel.mention}.",
                ephemeral=True,
            )


    # Botão que abre o menu de seleção
    class RegisterButton(Button):
        def __init__(self, custom_id):
            super().__init__(label="Cadastrar Venda", style=discord.ButtonStyle.primary, custom_id=custom_id)

        async def callback(self, interaction: discord.Interaction):
            view = BotClient.SelectionMenuView()
            await interaction.response.send_message("Por favor, selecione o tipo de remédio:", view=view, ephemeral=True)

    # Menu de seleção (Dropdown)
    class SelectionMenuView(View):
        def __init__(self):
            super().__init__(timeout=None)  
            self.add_item(BotClient.SelectionMenu())

    class SelectionMenu(discord.ui.Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="Dorfrex"),
                discord.SelectOption(label="Paracetamil"),
                discord.SelectOption(label="Voltarom"),
            ]
            super().__init__(placeholder="Selecione o tipo de remédio...", options=options, custom_id="select_medicine")

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.send_modal(BotClient.RegistrationForm(self.values[0]))
    


    # Modal (Formulário)
    class RegistrationForm(Modal):
        def __init__(self, category):
            super().__init__(title=f"Cadastro - {category}")
            self.category = category

            self.idcliente = TextInput(label="ID DO CLIENTE")
            self.name = TextInput(label="NOME DO CLIENTE", style=discord.TextStyle.short)
            self.quantity = TextInput(label="QUANTIDADE")
            self.valor = TextInput(label="VALOR RECEBIDO")

            self.add_item(self.idcliente)
            self.add_item(self.name)
            self.add_item(self.quantity)
            self.add_item(self.valor)

        async def on_submit(self, interaction: discord.Interaction):
            # Validações dos campos
            if not self.idcliente.value.isdigit():
                await interaction.response.send_message("⚠️ O ID do cliente deve conter apenas números.", ephemeral=True)
                return

            if not self.quantity.value.isdigit():
                await interaction.response.send_message("⚠️ A quantidade deve ser um número válido.", ephemeral=True)
                return

            try:
                valor_float = float(self.valor.value)
                if valor_float <= 0:
                    await interaction.response.send_message("⚠️ O valor recebido deve ser maior que zero.", ephemeral=True)
                    return
            except ValueError:
                await interaction.response.send_message("⚠️ O valor recebido deve ser um número válido.", ephemeral=True)
                return

            registro = (
                f"--------------------------------------------\n"
                f"**Venda cadastrada por: {interaction.user.mention}**\n"
                f"- **ID Cliente**: {self.idcliente.value}\n"
                f"- **Cliente**: {self.name.value}\n"
                f"- **Quantidade**: {self.quantity.value}\n"
                f"- **Remédio**: {self.category}\n"
                f"- **Valor Recebido**: R$ {float(self.valor.value):,.2f}\n"
                f"--------------------------------------------\n"
                f"📅 Data/Hora: {datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y - %H:%M:%S')}"
            )

            data_hora = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y • %H:%M:%S')
            vendedor = interaction.user.mention

            embed = interaction.client.create_register_embed(
                id_cliente=self.idcliente.value,
                cliente=self.name.value,
                quantidade=self.quantity.value,
                remedio=self.category,
                valor_recebido=float(self.valor.value),
                vendedor=vendedor,
                data_hora=data_hora,
            )

            await interaction.response.send_message(f"✅ Venda cadastrada com sucesso!\n{registro}", ephemeral=True)

            # Envia o relatório para o canal de registros
            registro_channel = interaction.client.get_channel(id_do_canal_registros)
            if registro_channel:
                await registro_channel.send(embed=embed)

            else:
                print(f"Erro: Canal de registros com ID {id_do_canal_registros} não encontrado.")

            outro_canal_registro = interaction.client.get_channel(id_do_canal_registros2)
            if outro_canal_registro:
                await outro_canal_registro.send(registro)
            else:
                print(f"Erro: Canal de relatórios com ID {id_do_canal_registros2} não encontrado.")

    # Cria um embed para o relatório no canal de registros
    def create_register_embed(self, id_cliente, cliente, quantidade, remedio, valor_recebido, vendedor, data_hora):
        embed = discord.Embed(
            title="📋 Relatório da Venda\n\u200b",
            color=discord.Colour(value=0xB90E0A)  
        )
        embed.add_field(name="ID Cliente", value=id_cliente, inline=True)
        embed.add_field(name="Cliente", value=cliente, inline=True)
        embed.add_field(name="Remédio", value=remedio, inline=True)
        embed.add_field(name="Quantidade", value=f"{quantidade}\n\u200b", inline=True)
        embed.add_field(name="Valor Recebido", value=f"R$ {valor_recebido:,.0f}", inline=True)
        embed.add_field(name="Vendedor", value=f"{vendedor}\n\u200b", inline=True)
        #embed.add_field(name="Data/Hora", value=data_hora, inline=False)

        #embed.set_footer(text=f"📅 Data: {data_hora} • Verificado: HP")
        embed.set_footer(text=f"📅 {data_hora}")
        return embed

    class ControlButton(Button):
        def __init__(self, custom_id):
            super().__init__(label="Consultar ID", style=discord.ButtonStyle.secondary, custom_id=custom_id)

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.send_modal(BotClient.ClientSearchModal())


    # Modal de pesquisa do cliente
    class ClientSearchModal(Modal):
        def __init__(self):
            super().__init__(title="Consulta de ID Cliente")
            self.client_id = TextInput(label="ID DO CLIENTE", style=discord.TextStyle.short)
            self.add_item(self.client_id)

        async def on_submit(self, interaction: discord.Interaction):
            client_id = self.client_id.value.strip()

            if not client_id.isdigit():
                await interaction.response.send_message("⚠️ O ID do cliente deve conter apenas números.", ephemeral=True)
                return

            total_quantity = await interaction.client.search_client_sales(client_id, interaction.client)

            laudo_message, laudos_quantity = await interaction.client.search_client_laudo(client_id, interaction.client)

            max_quantity = 100 + laudos_quantity 
            remaining_quantity = max_quantity - total_quantity if total_quantity is not None else max_quantity

            embed = discord.Embed(
                title="Resultado da Consulta\n\u200b",
                color=discord.Colour(value=0xB90E0A)
            )
        
            if total_quantity is not None:
                embed.add_field(name="✅ Compras Encontradas", value=f"O cliente com ID {client_id} comprou um total de {total_quantity} remédios.", inline=False)
            else:
                embed.add_field(name="⚠️ Nenhuma Compra", value=f"Não foi encontrada nenhuma venda para o ID {client_id}.", inline=False)
        
            if laudo_message:
                embed.add_field(name="📄 Laudo Encontrado", value=laudo_message, inline=False)
            else:
                embed.add_field(name="⚠️ Laudo", value=f"Não há laudo encontrado para o cliente ID {client_id}.", inline=False)

            embed.add_field(name="💊 Quantidade Restante", value=f"O cliente ainda pode comprar {remaining_quantity} remédios.", inline=False)
        
            await interaction.response.send_message(embed=embed, ephemeral=True)

    # Função para buscar o laudo de um cliente no canal de laudos (utilizando SALE2_REGEX)
    async def search_client_laudo(self, client_id: str, client: discord.Client):

        laudo_channel = client.get_channel(id_canal_laudosrg)
        if not laudo_channel:
            print(f"Erro: Canal de laudos com ID {id_canal_laudosrg} não encontrado.")
            return None, 0
        
        total_quantity = 0
        found_laudos = []

        async for message in laudo_channel.history(limit=100):  
            print(f"Lendo mensagem de laudo: {message.content}")  

            # Ajuste do regex para a nova definição (SALE2_REGEX)
            match = SALE2_REGEX.search(message.content)

            if match:
                msg_client_id = match.group(2)
                quantity = int(match.group(3))
                date = match.group(4)

                print(f"Encontrado - ID: {msg_client_id}, Quantidade: {quantity}, Data: {date}")

                if msg_client_id == client_id:
                    total_quantity += quantity
                    found_laudos.append(f"{quantity} remédios em {date}")

        if found_laudos:
            laudo_message = f"Cliente de ID {client_id} tem um total de {total_quantity} remédios registrados nos seguintes laudos:\n - " + "\n - ".join(found_laudos)
            return laudo_message, total_quantity
        
        return None, 0

    




    # Função para buscar e somar as vendas do cliente no canal de registros
    async def search_client_sales(self, client_id: str, client: discord.Client):
        total_quantity = 0

        # Acessa o canal de registros
        registro_channel = client.get_channel(id_do_canal_registros2)
        if not registro_channel:
            print(f"Erro: Canal de registros com ID {id_do_canal_registros2} não encontrado.")
            return None

        async for message in registro_channel.history(limit=150): 
            print(f"Lendo mensagem: {message.content}")  

            match = re.search(
                r"\*\*ID Cliente\*\*\s*[:\-]?\s*(\d+).*?\*\*Quantidade\*\*\s*[:\-]?\s*(\d+)",
                message.content,
                re.DOTALL
            )

            if match:
                msg_client_id = match.group(1)
                quantity = int(match.group(2))

                print(f"Encontrado - ID: {msg_client_id}, Quantidade: {quantity}")

                if msg_client_id == client_id:
                    total_quantity += quantity

        if total_quantity > 0:
            return total_quantity
        else:
            return None

    
    # Laudos -------------------------------------------------------------
    class LaudoButton(Button):
        def __init__(self, custom_id):
            super().__init__(label="Lançar Laudo", style=discord.ButtonStyle.primary, custom_id=custom_id)

        async def callback(self, interaction: discord.Interaction):
            # Abre a modal para o usuário preencher os dados
            modal = BotClient.LaudoModal()
            await interaction.response.send_modal(modal)

    class LaudoModal(Modal):
        def __init__(self):
            super().__init__(title="Registro de Laudo")

            # Criação dos campos de entrada (ID do cliente e Quantidade de Remédios)
            self.add_item(TextInput(label="ID do Cliente", required=True))
            self.add_item(TextInput(label="Quantidade de Remédios", required=True))

        async def on_submit(self, interaction: discord.Interaction):
            # Recupera os dados fornecidos pelo usuário
            id_cliente = self.children[0].value
            qnt_remedios = self.children[1].value

            # Validação do ID do Cliente (deve ser numérico)
            if not id_cliente.isdigit():
                await interaction.response.send_message("⚠️ Erro: O ID do cliente deve conter apenas números.", ephemeral=True)
                return

            # Validação da Quantidade de Remédios (deve ser um valor válido)
            valores_validos = ["200", "400", "600", "800", "1000"]
            if qnt_remedios not in valores_validos:
                await interaction.response.send_message("⚠️ Erro: Não existe essa quantidade de remédios para laudos.", ephemeral=True)
                return

            # Cria o relatório simples
            # Formata os dados cadastrados se estiverem válidos
            relatorio = (
                f"--------------------------------------------\n"
                f"**Laudo lançado por: {interaction.user.mention}**\n"
                f"- **ID do Cliente**: {id_cliente}\n"
                f"- **Quantidade de Remédios**: {qnt_remedios}\n"
                f"--------------------------------------------\n"
                f"📅 Data/Hora: {datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y - %H:%M:%S')}"
            )
            #relatorio = f"**Laudo Gerado**\nID DO CLIENTE: {id_cliente}\nQUANTIDADE DE REMÉDIOS: {qnt_remedios}"

            # Envia o relatório para o canal específico (id_canal_laudosrg)
            laudosreg_channel = interaction.guild.get_channel(id_canal_laudosrg)
            if laudosreg_channel is None:
                await interaction.response.send_message("Erro: Canal de Laudos não encontrado.", ephemeral=True)
            else:
                await laudosreg_channel.send(relatorio)
                await interaction.response.send_message(f"Laudo gerado com sucesso! Relatório enviado para {laudosreg_channel.mention}", ephemeral=True)

    class LaudoView(View):
        def __init__(self):
            super().__init__()
            self.add_item(LaudoButton())


    def create_button_view(self):
        view = View(timeout=None) 
        view.add_item(self.RegisterButton(custom_id="register_sale")) 
        view.add_item(self.AbrirTicketButton(custom_id="abrir_ticket"))  
        return view

    def create_control_view(self):
        view = View(timeout=None)
        view.add_item(BotClient.ControlButton(custom_id="consult_id"))
        return view

    def create_laudos_button_view(self):
        view = View(timeout=None)
        view.add_item(self.LaudoButton(custom_id="launch_laudo"))
        return view
    


# Regex para extrair dados das mensagens
SALE_REGEX = re.compile(
    r"\*\*Venda cadastrada por: <@(\d+)>\*\*.*?"
    r"\*\*ID Cliente\*\*\s*[:\-]?\s*(\d+).*?"
    r"\*\*Quantidade\*\*\s*[:\-]?\s*(\d+).*?"
    r"\*\*Valor Recebido\*\*\s*[:\-]?\s*R\$\s*([\d\.,]+).*?"
    r"📅 Data/Hora: (\d{2}/\d{2}/\d{4})",
    re.DOTALL
)

# Regex para busca de laudo com Data/Hora
SALE2_REGEX = re.compile(
    r"\*\*Laudo lançado por: <@(\d+)>\*\*.*?" 
    r"\*\*ID do Cliente\*\*\s*[:\-]?\s*(\d+).*?" 
    r"\*\*Quantidade de Remédios\*\*\s*[:\-]?\s*(\d+).*?" 
    r"📅 Data/Hora: (\d{2}/\d{2}/\d{4})", 
    re.DOTALL
)


aclient = BotClient()
tree = app_commands.CommandTree(aclient)

@tree.command(guild = discord.Object(id=id_do_servidor), name = 'cobrança', description='Faça a cobrança em um intervalo de datas...') #Comando específico para seu servidor

async def slash2(interaction: discord.Interaction, data_inicio: str, data_fim: str):
    """
    Filtra as vendas de uma data específica e agrupa os valores por usuário.
    """
    try:
        data_inicio = datetime.strptime(data_inicio, "%d/%m/%Y")
        data_fim = datetime.strptime(data_fim, "%d/%m/%Y")

        if data_inicio > data_fim:
            await interaction.response.send_message(
                "⚠️ A data de início não pode ser maior que a data de fim.", ephemeral=True
            )
            return
    except ValueError:
        await interaction.response.send_message(
            "⚠️ Data inválida! Use o formato DD/MM/AAAA.", ephemeral=True
        )
        return

    registro_channel = interaction.client.get_channel(id_do_canal_registros2)
    if not registro_channel:
        await interaction.response.send_message(
            "⚠️ Canal de registros não encontrado.", ephemeral=True
        )
        return

    vendas_por_usuario = {}

    async for message in registro_channel.history(limit=200):  
        match = SALE_REGEX.search(message.content)

        if match:
            user_id, _, quantity, value_received, sale_date = match.groups()
            sale_date = datetime.strptime(sale_date, "%d/%m/%Y")

            if data_inicio <= sale_date <= data_fim:
                quantity = int(quantity)
                value_received = float(value_received.replace(",", "").replace(".", "")) / 100

                if user_id not in vendas_por_usuario:
                    vendas_por_usuario[user_id] = {"quantidade_total": 0, "valor_total": 0}

                vendas_por_usuario[user_id]["quantidade_total"] += quantity
                vendas_por_usuario[user_id]["valor_total"] += value_received

    if data_inicio == data_fim:
        titulosemvendas = f"📋 Cobrança - {data_inicio.strftime('%d/%m/%Y')}\n\u200b"
    else:
        titulosemvendas = f"📋 Cobrança - {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}\n\u200b"

    if not vendas_por_usuario:
        embed = discord.Embed(
            title=titulosemvendas,
            description="❌ Nenhuma venda encontrada no intervalo especificado.\n\u200b",
            color=discord.Colour(value=0xFF0000)  # Vermelho
        )
        nowdate = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%H:%M:%S')
        embed.set_footer(text=f"Hoje às {nowdate}")
        await interaction.response.send_message(embed=embed)
        return

    if data_inicio == data_fim:
        titulo = f"📋 Cobrança - {data_inicio.strftime('%d/%m/%Y')}\n\u200b"
    else:
        titulo = f"📋 Cobrança - {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}\n\u200b"

    embed = discord.Embed(
        #title=f"📋Cobrança - {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}\n\u200b",
        title=titulo,
        color=discord.Colour(value=0xB90E0A)  
    )

    for user_id, dados in vendas_por_usuario.items():
        quantidade_total = dados["quantidade_total"]
        valor_total = dados["valor_total"]
        #imposto_total = valor_total * 0.35

        imposto_percentual = percentuais_personalizados.get(int(user_id), 0.35)
        imposto_total = valor_total * imposto_percentual

        #user = await interaction.client.fetch_user(user_id)
        #user_name = user.name  # Pega o nome de usuário (nome de exibição)

        guild = interaction.guild  
        member = await guild.fetch_member(user_id)
        #user_id = member.id

        nickname = member.nick if member.nick else member.display_name

        embed.add_field(
            name=f"**Usuário:** {nickname} ",
            value=(
                f"**Quantidade Total:** {quantidade_total}\n"
                f"**Valor Total:** R$ {valor_total:,.0f}\n"
                f"**Imposto Total:** R$ {imposto_total:,.0f}\n"
                f"\u200b"  
            ),
            inline=False
        )
        nowdate = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%H:%M:%S')
        embed.set_footer(text=f"Hoje às {nowdate}")


    await interaction.response.send_message(embed=embed)

# =========================== Comando para alterar porcentagem ===========================
@tree.command(guild=discord.Object(id=id_do_servidor), name="alterar_porcentagem", description="altere a porcentagem de imposto para um usuário...")
async def alterar_porcentagem(interaction: discord.Interaction, usuario: discord.User, nova_porcentagem: float):
    """
    Altera a porcentagem de imposto para o usuário especificado.
    """
    if nova_porcentagem < 0 or nova_porcentagem > 1:
        await interaction.response.send_message("⚠️ Porcentagem inválida! Use um valor entre 0 e 1.", ephemeral=True)
        return

    percentuais_personalizados[usuario.id] = nova_porcentagem

    await interaction.response.send_message(
        f"✅ Porcentagem de imposto para {usuario.mention} atualizada para {nova_porcentagem * 100:.2f}%.",
        ephemeral=True
    )

# =========================== Comando para listar porcentagens ===========================
@tree.command(guild=discord.Object(id=id_do_servidor), name="ver_porcentagens", description="Veja as porcentagens de imposto alteradas.")
async def ver_porcentagens(interaction: discord.Interaction):
    """
    Mostra as porcentagens de imposto alteradas para os usuários.
    """
    await interaction.response.defer(ephemeral=True)

    if not percentuais_personalizados:
        await interaction.followup.send("ℹ️ Nenhuma porcentagem foi alterada até o momento.")
        return

    mensagens = []
    guild = interaction.guild 

    for user_id, porcentagem in percentuais_personalizados.items():
        try:
            member = await guild.fetch_member(user_id)
            nickname = member.nick if member.nick else member.display_name
        except Exception:
            nickname = f"ID {user_id}"  

        mensagens.append(f"**{nickname}**: {porcentagem * 100:.2f}%")

    resultado = "\n".join(mensagens)

    await interaction.followup.send(f"📊 **Porcentagens de imposto alteradas:**\n\n{resultado}")




def criar_embed_meta(usuario: discord.User, meta: int, progresso: int) -> discord.Embed:
    embed = discord.Embed(
        title="📈 Meta de Farme\u200b",
        description=f"**Usuário:** {usuario.mention}\n**Meta:** {meta} matérias\n**Progresso:** {progresso}/{meta} matérias\u200b",
        color=discord.Colour(value=0xB90E0A)  
    )
    embed.set_thumbnail(url=usuario.avatar.url if usuario.avatar else discord.Embed.Empty)
    embed.set_footer(text="Atualizado automaticamente ao enviar farme.")
    return embed

# =========================== Comando para definir a meta ===========================
@tree.command(guild=discord.Object(id=id_do_servidor), name="definir_meta", description="Defina a meta de farme para um usuário.")
async def definir_meta(interaction: discord.Interaction, usuario: discord.User, meta: int):
    if meta <= 0:
        await interaction.response.send_message("⚠️ A meta deve ser maior que 0.", ephemeral=True)
        return

    metas[usuario.id] = meta
    farme_parcial[usuario.id] = 0  

    canal_metas = interaction.client.get_channel(id_canal_metas)
    if not canal_metas:
        await interaction.response.send_message("⚠️ O canal de metas não foi encontrado.", ephemeral=True)
        return

    embed = criar_embed_meta(usuario, meta, 0)
    
    if usuario.id in mensagens_metas:  
        msg_id = mensagens_metas[usuario.id]
        try:
            mensagem = await canal_metas.fetch_message(msg_id)
            await mensagem.edit(embed=embed)
        except discord.NotFound:
            mensagem = await canal_metas.send(embed=embed)
            mensagens_metas[usuario.id] = mensagem.id
    else:  
        mensagem = await canal_metas.send(embed=embed)
        mensagens_metas[usuario.id] = mensagem.id

    await interaction.response.send_message(f"✅ Meta definida para {usuario.mention}.", ephemeral=True)


async def buscar_meta_no_canal(usuario: discord.User, interaction: discord.Interaction) -> int:
    """
    Busca a meta de farme de um usuário no canal de metas.

    Args:
        usuario (discord.User): O usuário cuja meta será buscada.
        interaction (discord.Interaction): A interação do comando.

    Returns:
        int: A meta encontrada. Retorna 0 se não encontrar.
    """
    canal_metas = interaction.client.get_channel(id_canal_metas)
    if not canal_metas:
        print("⚠️ Canal de metas não encontrado.")
        return 0

    async for mensagem in canal_metas.history(limit=100):
        if mensagem.author == interaction.client.user and mensagem.embeds:
            embed = mensagem.embeds[0]
            descricao = embed.description

            if f"**Usuário:** {usuario.mention}" in descricao:
                meta = int(descricao.split("**Meta:**")[1].split("matérias")[0].strip())
                return meta
    return 0

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def carregar_progresso_do_canal(canal_metas: discord.TextChannel) -> dict:
    """
    Recarrega o progresso dos usuários no canal de metas.

    Args:
        canal_metas (discord.TextChannel): O canal de metas.

    Returns:
        dict: Um dicionário com os IDs dos usuários e seus respectivos progressos.
    """
    progresso_atual = {}
    async for mensagem in canal_metas.history(limit=100):
        if mensagem.author == aclient.user and mensagem.embeds:
            embed = mensagem.embeds[0]
            descricao = embed.description
            if "**Usuário:**" in descricao and "**Progresso:**" in descricao:
                usuario_id = int(descricao.split("**Usuário:** ")[1].split("<@")[1].split(">")[0].replace("!", ""))
                progresso = int(descricao.split("**Progresso:** ")[1].split("/")[0].strip())
                progresso_atual[usuario_id] = progresso
    return progresso_atual


# =========================== Comando para enviar farme ===========================
@tree.command(guild=discord.Object(id=id_do_servidor), name="enviar_farme", description="Envie a quantidade de matérias farmeadas.")
async def enviar_farme(interaction: discord.Interaction, quantidade: int):
    if quantidade <= 0:
        await interaction.response.send_message("⚠️ A quantidade deve ser maior que 0.", ephemeral=True)
        logging.warning(f"Usuário {interaction.user.id} tentou enviar quantidade inválida: {quantidade}.")
        return

    usuario = interaction.user
    logging.info(f"Iniciando envio de farme para usuário {usuario.id} com quantidade {quantidade}.")

    try:
        meta = await buscar_meta_no_canal(usuario, interaction)
        if meta == 0:
            await interaction.response.send_message("⚠️ Nenhuma meta foi definida para você.", ephemeral=True)
            logging.warning(f"Nenhuma meta encontrada para o usuário {usuario.id}.")
            return

        canal_aprovacao = interaction.client.get_channel(id_canal_aprovacao)
        if not canal_aprovacao:
            await interaction.response.send_message("⚠️ Canal de aprovação não encontrado.", ephemeral=True)
            logging.error("Canal de aprovação não foi encontrado.")
            return

        embed_solicitacao = discord.Embed(
            title="🕐 Solicitação de Aprovação de Farm",
            description=f"**Usuário:** {usuario.mention}\n"
                        f"**Quantidade Solicitada:** {quantidade}\n"
                        f"**Meta Atual:** {meta}",
            color=discord.Colour(value=0xB90E0A)
        )
        mensagem_aprovacao = await canal_aprovacao.send(embed=embed_solicitacao)

        await mensagem_aprovacao.add_reaction("✅")  
        await mensagem_aprovacao.add_reaction("❌")  

        await interaction.response.send_message("📨 Sua solicitação foi enviada para aprovação.", ephemeral=True)

        logging.info(f"Solicitação enviada para aprovação no canal {id_canal_aprovacao}.")

    except Exception as e:
        logging.error(f"Erro durante o envio de solicitação de farme para o usuário {usuario.id}: {e}")
        await interaction.response.send_message("⚠️ Ocorreu um erro ao enviar o farme. Tente novamente mais tarde.", ephemeral=True)


# =========================== Evento de Reação para Aprovação ===========================
@aclient.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.channel_id != id_canal_aprovacao:
        return

    if payload.member.bot:
        return

    canal_aprovacao = aclient.get_channel(payload.channel_id)
    mensagem = await canal_aprovacao.fetch_message(payload.message_id)
    embed = mensagem.embeds[0] if mensagem.embeds else None

    if not embed or embed.title != "🕐 Solicitação de Aprovação de Farm":
        return

    usuario_mencao = embed.description.split("**Usuário:** ")[1].split("\n")[0]
    quantidade = int(embed.description.split("**Quantidade Solicitada:** ")[1].split("\n")[0].strip())
    meta = int(embed.description.split("**Meta Atual:** ")[1].strip())

    usuario_id = int(usuario_mencao.replace("<@", "").replace(">", "").replace("!", ""))

    if str(payload.emoji) == "✅":  
        logging.info(f"Solicitação aprovada para usuário {usuario_id}.")

        canal_metas = aclient.get_channel(id_canal_metas)
        progresso_atual = await carregar_progresso_do_canal(canal_metas)  
        progresso = progresso_atual.get(usuario_id, 0) + quantidade

        usuario = await aclient.fetch_user(usuario_id)
        embed_atualizado = criar_embed_meta(usuario, meta, progresso)

        async for mensagem_meta in canal_metas.history(limit=100):
            if mensagem_meta.author == aclient.user and mensagem_meta.embeds:
                embed_existente = mensagem_meta.embeds[0]
                if f"**Usuário:** {usuario.mention}" in embed_existente.description:
                    await mensagem_meta.edit(embed=embed_atualizado)
                    break

        embed_resposta = discord.Embed(
            title="Solicitação Aprovada",
            description=f"✅ Solicitação aprovada por {payload.member.mention} e progresso atualizado para {usuario.mention}.",
            color=discord.Color.green()
        )
        await mensagem.reply(embed=embed_resposta, mention_author=False)

    elif str(payload.emoji) == "❌": 
        logging.info(f"Solicitação rejeitada para usuário {usuario_id}.")
        embed_resposta = discord.Embed(
            title="Solicitação Rejeitada",
            description=f"❌ Solicitação rejeitada por {payload.member.mention} para {usuario_mencao}.",
            color=discord.Color.red()
        )
        await mensagem.reply(embed=embed_resposta, mention_author=False)



# =========================== Comando para ID's repetidos ===========================
@tree.command(guild=discord.Object(id=id_do_servidor), name="ids_repetidos", description="Lista os IDs de clientes repetidos e as quantidades vendidas.")
async def ids_repetidos(interaction: discord.Interaction):
    """
    Busca IDs repetidos no canal de registros e soma as quantidades associadas.
    """
    id_quantidades = defaultdict(int)  
    id_ocorrencias = defaultdict(int)  

    registro_channel = interaction.client.get_channel(id_do_canal_registros2)
    if not registro_channel:
        await interaction.response.send_message("⚠️ Canal de registros não encontrado.", ephemeral=True)
        return

    async for message in registro_channel.history(limit=150):  
        match = re.search(
            r"\*\*ID Cliente\*\*\s*[:\-]?\s*(\d+).*?\*\*Quantidade\*\*\s*[:\-]?\s*(\d+)",
            message.content,
            re.DOTALL
        )

        if match:
            msg_client_id = match.group(1)  
            quantity = int(match.group(2))  

            id_quantidades[msg_client_id] += quantity
            id_ocorrencias[msg_client_id] += 1

    ids_repetidos = {
        id_: qtd for id_, qtd in id_quantidades.items() if id_ocorrencias[id_] >= 2
    }

    if not ids_repetidos:
        await interaction.response.send_message("✅ Nenhum ID repetido encontrado.", ephemeral=True)
        return

    embed = discord.Embed(
        title="IDs Repetidos e Quantidades Vendidas",
        color=discord.Colour(value=0xB90E0A)
    )
    for client_id, total_qtd in ids_repetidos.items():
        embed.add_field(
            name=f"ID Cliente: {client_id}",
            value=f"Quantidade Total: {total_qtd}",
            inline=False
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)

# =========================== Comando para IDs com vendas acima de 100 ===========================
@tree.command(guild=discord.Object(id=id_do_servidor), name="verificar_vendas", description="Verifica se houve vendas para IDs com quantidade acima de 100.")
async def verificar_vendas(interaction: discord.Interaction):
    """
    Verifica vendas acima de 100 no canal de registros.
    """
    vendas_acima = defaultdict(list)  

    # Acessa o canal de registros
    registro_channel = interaction.client.get_channel(id_do_canal_registros2)
    if not registro_channel:
        await interaction.response.send_message("⚠️ Canal de registros não encontrado.", ephemeral=True)
        return

    async for message in registro_channel.history(limit=150):  
        match = re.search(
            r"\*\*ID Cliente\*\*\s*[:\-]?\s*(\d+).*?\*\*Quantidade\*\*\s*[:\-]?\s*(\d+)",
            message.content,
            re.DOTALL
        )

        if match:
            msg_client_id = match.group(1)  
            quantity = int(match.group(2))  
            if quantity > 100:
                vendas_acima[msg_client_id].append(quantity)  

    if not vendas_acima:
        await interaction.response.send_message("✅ Nenhuma venda acima de 100 foi encontrada.", ephemeral=True)
        return

    embed = discord.Embed(
        title="IDs com Vendas Acima de 100",
        color=discord.Colour(value=0xB90E0A)
    )
    for client_id, quantities in vendas_acima.items():
        quantities_str = ", ".join(map(str, quantities))
        embed.add_field(
            name=f"ID Cliente: {client_id}",
            value=f"Quantidades Vendidas: {quantities_str}",
            inline=False
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(guild=discord.Object(id=id_do_servidor), name="listar_metas", description="Lista os usuários e o status de suas metas.")
async def listar_metas(interaction: discord.Interaction):
    try:
        canal_metas = interaction.client.get_channel(id_canal_metas)
        if not canal_metas:
            await interaction.response.send_message("⚠️ Canal de metas não encontrado.", ephemeral=True)
            logging.error("Canal de metas não foi encontrado.")
            return

        lista_alcancaram_meta = []
        lista_nao_alcancaram_meta = []

        async for mensagem_meta in canal_metas.history(limit=100):
            if mensagem_meta.author == interaction.client.user and mensagem_meta.embeds:
                embed = mensagem_meta.embeds[0]

                if "**Usuário:**" in embed.description and "**Progresso:**" in embed.description and "**Meta:**" in embed.description:
                    usuario_mencao = embed.description.split("**Usuário:** ")[1].split("\n")[0]
                    progresso_str = embed.description.split("**Progresso:** ")[1].split("\n")[0].strip()
                    meta_str = embed.description.split("**Meta:** ")[1].strip()

                    try:
                        progresso = int(progresso_str.split("/")[0].strip())  
                        meta = int(meta_str.split(" ")[0].strip()) 

                        if "] " in usuario_mencao:
                            primeiro_nome = usuario_mencao.split("] ")[1].split(" |")[0]
                        else:
                            primeiro_nome = usuario_mencao  

                        if progresso >= meta:
                            lista_alcancaram_meta.append(f"- **{primeiro_nome}**: Farmou {progresso}/{meta}")
                        else:
                            lista_nao_alcancaram_meta.append(f"- **{primeiro_nome}**: Farmou {progresso}/{meta}")

                    except ValueError:
                        logging.warning(f"Falha ao processar progresso ou meta no embed: {embed.description}")
                        continue  

        resposta = "**📋 Relatório de Metas:**\n\n"
        if lista_alcancaram_meta:
            resposta += "**✅ Usuários que alcançaram ou ultrapassaram suas metas:**\n" + "\n".join(lista_alcancaram_meta) + "\n\n"
        else:
            resposta += "**✅ Usuários que alcançaram ou ultrapassaram suas metas:**\nNenhum usuário alcançou a meta.\n\n"

        if lista_nao_alcancaram_meta:
            resposta += "**❌ Usuários que ainda não concluíram suas metas:**\n" + "\n".join(lista_nao_alcancaram_meta)
        else:
            resposta += "**❌ Usuários que ainda não concluíram suas metas:**\nTodos os usuários concluíram suas metas."

        await interaction.response.send_message(resposta, ephemeral=False)
        logging.info("Relatório de metas enviado.")

    except Exception as e:
        logging.error(f"Erro ao listar metas: {e}")
        await interaction.response.send_message("⚠️ Ocorreu um erro ao gerar o relatório. Tente novamente mais tarde.", ephemeral=True)


# =========================== Comando para gerar relatório semanal ===========================
@tree.command(
    guild=discord.Object(id=id_do_servidor),
    name='relatorio',
    description='Gere um relatório semanal personalizado'
)
async def relatorio(interaction: discord.Interaction,
                    bateram_meta: str,
                    justificaram: str,
                    nao_justificaram: str,
                    promovidos: str,
                    porcentagens: str):
    """
    Gera um relatório semanal preenchendo as categorias fornecidas pelo usuário.
    """
    def formatar_lista(lista):
        return '\n'.join([f'・{item}' for item in lista.split(", ")]) if lista else "Nenhum registrado."

    async def buscar_metas_alcancadas():
        canal_metas = interaction.client.get_channel(id_canal_metas)
        if not canal_metas:
            return "Nenhum registrado."

        lista_alcancaram_meta = []

        async for mensagem_meta in canal_metas.history(limit=100):
            if mensagem_meta.author == interaction.client.user and mensagem_meta.embeds:
                embed = mensagem_meta.embeds[0]
                if "**Usuário:**" in embed.description and "**Progresso:**" in embed.description and "**Meta:**" in embed.description:
                    usuario_mencao = embed.description.split("**Usuário:** ")[1].split("\n")[0]
                    progresso_str = embed.description.split("**Progresso:** ")[1].split("\n")[0].strip()
                    meta_str = embed.description.split("**Meta:** ")[1].strip()

                    try:
                        progresso = int(progresso_str.split("/")[0].strip())
                        meta = int(meta_str.split(" ")[0].strip())

                        if progresso >= meta:
                            usuario_id = int(usuario_mencao.replace('<@', '').replace('>', '').replace('!', ''))

                            membro = await interaction.guild.fetch_member(usuario_id)

                            apelido = membro.display_name
                            lista_alcancaram_meta.append(f'・{apelido}')
                    except (ValueError, discord.NotFound):
                        continue
        return '\n'.join(lista_alcancaram_meta) if lista_alcancaram_meta else "Nenhum registrado."


    metas_alcancadas = await buscar_metas_alcancadas()

    embed = discord.Embed(
        title="📊 Relatório Semanal = Farmácia",
        description="Resumo das metas e status dos usuários",
        color=discord.Colour(value=0xB90E0A)
    )

    embed.add_field(
        name="🏆 Usuários que alcançaram ou ultrapassaram suas metas:",
        value=metas_alcancadas,
        inline=False
    )

    embed.add_field(
        name="📈 Bateram meta de vendas:",
        value=formatar_lista(bateram_meta),
        inline=False
    )

    embed.add_field(
        name="✍️ Justificaram não bater meta de farm:",
        value=formatar_lista(justificaram),
        inline=False
    )

    embed.add_field(
        name="⚠️ Não pagaram a meta e não justificaram:",
        value=formatar_lista(nao_justificaram),
        inline=False
    )

    embed.add_field(
        name="📢 Promovidos da semana:",
        value=formatar_lista(promovidos),
        inline=False
    )

    embed.add_field(
        name="📊 Porcentagens atualizadas:",
        value=formatar_lista(porcentagens),
        inline=False
    )

    nowdate = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')
    embed.set_footer(text=f"Relatório gerado em: {nowdate}")

    await interaction.response.send_message(embed=embed)


@tree.command(
    guild=discord.Object(id=id_do_servidor),
    name='editar_relatorio',
    description='Edita um relatório existente'
)
async def editar_relatorio(interaction: discord.Interaction,
                           mensagem_id: str,
                           secao: str,
                           conteudo: str):
    """
    Edita um relatório existente, atualizando a seção especificada.
    """
    try:
        canal = interaction.channel
        mensagem = await canal.fetch_message(int(mensagem_id))

        if not mensagem.embeds:
            await interaction.response.send_message("⚠️ Mensagem fornecida não contém um embed.", ephemeral=True)
            return

        embed = mensagem.embeds[0]
        encontrou_secao = False

        secao_proc = secao.lower().strip()

        for i, field in enumerate(embed.fields):
            nome_secao_proc = field.name.lower().strip()

            if secao_proc in nome_secao_proc:
                encontrou_secao = True

                novos_itens = [f'・{nome.strip()}' for nome in conteudo.split(",")]
                novos_itens_formatados = "\n".join(novos_itens)

                novo_conteudo = field.value.strip() + "\n" + novos_itens_formatados
                embed.set_field_at(i, name=field.name, value=novo_conteudo, inline=False)

        if not encontrou_secao:
            await interaction.response.send_message("⚠️ Seção não encontrada no relatório. Confira o nome exato!", ephemeral=True)
            return

        await mensagem.edit(embed=embed)
        await interaction.response.send_message("✅ Relatório atualizado com sucesso!", ephemeral=True)

    except discord.NotFound:
        await interaction.response.send_message("⚠️ Mensagem não encontrada.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("⚠️ Permissões insuficientes para editar esta mensagem.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Erro ao editar o relatório: {e}", ephemeral=True)

# =========================== Comando para calcular novas metas ===========================
@tree.command(
    guild=discord.Object(id=id_do_servidor),
    name='calcular_metas',
    description='Calcula as novas metas de acordo com as vendas totais de cada usuário.'
)
async def calcular_metas(interaction: discord.Interaction, data_inicio: str, data_fim: str):
    """
    Calcula novas metas com base na quantidade total vendida por cada usuário.
    """
    await interaction.response.defer(ephemeral=True)

    try:
        data_inicio = datetime.strptime(data_inicio, "%d/%m/%Y")
        data_fim = datetime.strptime(data_fim, "%d/%m/%Y")

        if data_inicio > data_fim:
            await interaction.followup.send(
                "⚠️ A data de início não pode ser maior que a data de fim.", ephemeral=True
            )
            return
    except ValueError:
        await interaction.followup.send(
            "⚠️ Data inválida! Use o formato DD/MM/AAAA.", ephemeral=True
        )
        return

    registro_channel = interaction.client.get_channel(id_do_canal_registros2)
    if not registro_channel:
        await interaction.followup.send(
            "⚠️ Canal de registros não encontrado.", ephemeral=True
        )
        return

    vendas_por_usuario = {}

    async for message in registro_channel.history(limit=200):  
        match = SALE_REGEX.search(message.content)

        if match:
            user_id, _, quantity, value_received, sale_date = match.groups()
            sale_date = datetime.strptime(sale_date, "%d/%m/%Y")

            if data_inicio <= sale_date <= data_fim:
                quantity = int(quantity)

                if user_id not in vendas_por_usuario:
                    vendas_por_usuario[user_id] = 0

                vendas_por_usuario[user_id] += quantity

    if not vendas_por_usuario:
        await interaction.followup.send(
            f"⚠️ Não foram encontradas vendas no intervalo {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="📊 Novas Metas de Farm",
        description=f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
        color=discord.Colour(value=0xB90E0A)
    )

    # Calcula a nova meta para cada usuário
    for user_id, total_vendido in vendas_por_usuario.items():
        nova_meta = ((total_vendido / 50) * 165) + 2000

        guild = interaction.guild
        member = await guild.fetch_member(user_id)

        nickname = member.nick if member.nick else member.display_name

        embed.add_field(
            name=f"**Usuário:** {nickname}",
            value=(
                f"**Total Vendido:** {total_vendido}\n"
                f"**Nova Meta:** R$ {nova_meta:,.0f}\n"
                f"\u200b"  
            ),
            inline=False
        )

    nowdate = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%H:%M:%S')
    embed.set_footer(text=f"Relatório gerado às {nowdate}")

    await interaction.followup.send(embed=embed)




# =========================== Comando para excluir mensagens ===========================
@tree.command(
    guild=discord.Object(id=id_do_servidor),
    name='clear',
    description='Exclui mensagens do chat com base na quantidade ou entre datas especificadas.'
)
async def clear(interaction: discord.Interaction, quantidade: int = None, data_inicio: str = None, data_fim: str = None):
    """
    Exclui mensagens com base na quantidade ou em um intervalo de datas.
    """
    await interaction.response.defer(ephemeral=True)

    channel = interaction.channel

    if quantidade:
        if quantidade <= 0:
            await interaction.followup.send(
                "⚠️ A quantidade deve ser um número positivo!", ephemeral=True
            )
            return

        try:
            deleted = await channel.purge(limit=quantidade)
            
            await interaction.followup.send(
                f"🗑️ {len(deleted)} mensagem(s) excluída(s).", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "⚠️ Não tenho permissão para excluir mensagens neste canal!", ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"⚠️ Ocorreu um erro ao excluir mensagens: {str(e)}", ephemeral=True
            )
        return

    if data_inicio and data_fim:
        try:
            data_inicio = datetime.strptime(data_inicio, "%d/%m/%Y").replace(tzinfo=pytz.UTC)
            data_fim = datetime.strptime(data_fim, "%d/%m/%Y").replace(tzinfo=pytz.UTC)

            if data_inicio > data_fim:
                await interaction.followup.send(
                    "⚠️ A data de início não pode ser maior que a data de fim.", ephemeral=True
                )
                return

            data_fim += timedelta(days=1) - timedelta(seconds=1)

            deleted = []
            async for message in channel.history(limit=None):  
                if data_inicio <= message.created_at <= data_fim:
                    deleted.append(message)

            if deleted:
                for msg in deleted:
                    await msg.delete()

                await interaction.followup.send(
                    f"🗑️ {len(deleted)} mensagem(s) excluída(s) entre {data_inicio.strftime('%d/%m/%Y')} e {data_fim.strftime('%d/%m/%Y')}.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "⚠️ Nenhuma mensagem encontrada no intervalo especificado.", ephemeral=True
                )
        except ValueError:
            await interaction.followup.send(
                "⚠️ Datas inválidas! Use o formato DD/MM/AAAA.", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "⚠️ Não tenho permissão para excluir mensagens neste canal!", ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"⚠️ Ocorreu um erro ao excluir mensagens: {str(e)}", ephemeral=True
            )
        return

    await interaction.followup.send(
        "⚠️ Por favor, especifique uma quantidade ou intervalo de datas válido para excluir mensagens.",
        ephemeral=True
    )




# =========================== Comando para enviar ajustes ===========================
@tree.command(
    guild=discord.Object(id=id_do_servidor),
    name="enviar_ajuste",
    description="Envie uma mensagem privada para um usuário solicitando o ajuste da quantidade."
)
async def enviar_ajuste(
    interaction: discord.Interaction,
    usuario: discord.Member,
    quantidade: int
):
    """
    Envia uma mensagem privada para um usuário solicitando o ajuste da quantidade de matérias.
    """
    await interaction.response.defer(ephemeral=True)

    mensagem = (
        f"O estoque verificou seu envio e constatou que a quantidade de matérias está ***errada***, resultando na ***rejeição*** do seu farm. Por favor, reenvie no canal https://discord.com/channels/1316250142655123469/1319056492565102642 com o valor correto: {quantidade}.\n"
        "**Lembre-se de reenviar o mais rápido possível, para que seu farm seja validado e conste em sua meta!**"
    )

    try:
        await usuario.send(mensagem)
        await interaction.followup.send(f"✅ Mensagem enviada para {usuario.mention} com sucesso!")
    except Exception as e:
        await interaction.followup.send(
            f"❌ Não foi possível enviar a mensagem para {usuario.mention}. Erro: {e}"
        )


# =========================== Comando para fazer um relatório geral de vendas ===========================
# Atualizado com o novo REGEX
SALE3_REGEX = re.compile(
    r"\*\*Venda cadastrada por: <@(\d+)>\*\*.*?"
    r"\*\*ID Cliente\*\*\s*[:\-]?\s*(\d+).*?"
    r"\*\*Cliente\*\*\s*[:\-]?\s*([^\n]+).*?"
    r"\*\*Quantidade\*\*\s*[:\-]?\s*(\d+).*?"
    r"\*\*Remédio\*\*\s*[:\-]?\s*([^\n]+).*?"
    r"\*\*Valor Recebido\*\*\s*[:\-]?\s*R\$\s*([\d\.,]+).*?"
    r"📅 Data/Hora: (\d{2}/\d{2}/\d{4})\s*-\s*\d{2}:\d{2}:\d{2}",
    re.DOTALL
)

@tree.command(guild=discord.Object(id=id_do_servidor), name="relatorio_vendas", description="Gera um relatório detalhado de vendas.")
async def relatorio_vendas(interaction: discord.Interaction, data_inicio: str, data_fim: str):
    """
    Gera um relatório detalhado de vendas em um intervalo de datas e salva em um arquivo de texto.
    """
    try:
        data_inicio = datetime.strptime(data_inicio, "%d/%m/%Y")
        data_fim = datetime.strptime(data_fim, "%d/%m/%Y")

        if data_inicio > data_fim:
            await interaction.response.send_message("⚠️ A data de início não pode ser maior que a data de fim.", ephemeral=True)
            return
    except ValueError:
        await interaction.response.send_message("⚠️ Data inválida! Use o formato DD/MM/AAAA.", ephemeral=True)
        return


    await interaction.response.defer()

    registro_channel = interaction.client.get_channel(id_do_canal_registros2)  
    if not registro_channel:
        await interaction.followup.send("⚠️ Canal de registros não encontrado.", ephemeral=True)
        return

    vendas_por_usuario = {}

    async for message in registro_channel.history(limit=200):
        match = SALE3_REGEX.search(message.content)

        if match:
            user_id, id_cliente, cliente, quantidade, remedio, valor_recebido, data_venda = match.groups()
            data_venda = datetime.strptime(data_venda, "%d/%m/%Y")

            if data_inicio <= data_venda <= data_fim:
                valor_recebido = float(valor_recebido.replace(",", "").replace(".", "")) / 100
                quantidade = int(quantidade)

                if user_id not in vendas_por_usuario:
                    vendas_por_usuario[user_id] = {"nome": None, "vendas": []}

                vendas_por_usuario[user_id]["vendas"].append({
                    "id_cliente": id_cliente,
                    "cliente": cliente,
                    "quantidade": quantidade,
                    "remedio": remedio,
                    "valor_recebido": valor_recebido,
                    "data_venda": data_venda
                })

        file_path = "relatoriosvendas.txt"

    if not vendas_por_usuario:
        with open(file_path, "rb") as file:
            await interaction.followup.send(
                content=f"⚠️ **Não** foram encontradas vendas no intervalo {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}.\nO arquivo não foi alterado e está anexado abaixo:",
                file=discord.File(file, filename="relatoriosvendas.txt")
            )
        return

    relatorio_txt = []
    relatorio_txt.append(f"Relatório de Vendas de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}\n")
    relatorio_txt.append("=" * 30 + "\n")
    
    for user_id, dados in vendas_por_usuario.items():
        guild = interaction.guild
        member = await guild.fetch_member(user_id)
        nome_usuario = member.nick if member.nick else member.display_name
        vendas_por_usuario[user_id]["nome"] = nome_usuario

        relatorio_txt.append(f"Usuário: {nome_usuario}\n")
        for venda in dados["vendas"]:
            relatorio_txt.append(
                f"- ID Cliente: {venda['id_cliente']}\n"
                f"  Cliente: {venda['cliente']}\n"
                f"  Quantidade: {venda['quantidade']}\n"
                f"  Remédio: {venda['remedio']}\n"
                f"  Valor Recebido: R$ {venda['valor_recebido']:.2f}\n"
                f"  Data: {venda['data_venda'].strftime('%d/%m/%Y')}\n"
            )
        relatorio_txt.append("\n" + "=" * 30 + "\n")

    with open(file_path, "a", encoding="utf-8") as file:
        file.writelines("\n".join(relatorio_txt) + "\n")

    with open(file_path, "rb") as file:
        await interaction.followup.send(
            content="📋 Relatório gerado com sucesso! O arquivo foi atualizado e está anexado abaixo:",
            file=discord.File(file, filename="relatoriosvendas.txt")
        )

aclient.run('seu_token')
